from data_utils.aws.schema import Track,User,Manifest,Fav,Com,Base,make_session
import pandas as pd, numpy as np
import time

tables = dict(
    users = User,
    tracks = Track,
    manifest = Manifest,
    favs = Fav,
    coms = Com
    )

meta = Base.metadata

class table(object):
    """load a table('myTable') meta object by name, and then expose some useful vars"""
    def __init__(self,tablename):
        self.tablename = tablename
        self.table = meta.tables[tablename]
        self.colnames = self.table.columns.keys()
        self.keynames = self.table.primary_key.columns.keys()
        self.keyname = ','.join(self.keynames)
        self.keys = [i for i in self.table.primary_key.columns.items()]

class get(table):
    """get things from aws db w/meta"""
    def __init__(self,tablename):
        super().__init__(tablename)
        self.tablename = tablename
        self.keycols = [i for i in self.table.primary_key.columns]

    def ids(self,session):
        return session.query(*self.keycols).all()

    def all(self,session):
        return session.query(self.table).all()

    def columns(self,columns,session):
        cols = [self.table.columns[c] for c in columns]
        return session.query(columns).all()

    def next_null(self,column,session):
        return session.query(self.table).filter(
            self.table.columns[column]==None).limit(1).all()

    def extract(self,df,session,drop_exists=True):
        """ takes a processed df and drops rows if the id(s) are already in the sql dbase
            works with multiple primary keys and tries to speed up the process w/sets!
        """
        existing = self.ids(session)

        idmask = self.keynames
        names = df[idmask].columns
        vals = df[idmask].values

        #the magic list/tuple/set comprehension:
        new_ids = [i if tuple(i) not in existing else None for i in vals]

        new_ids = list(filter(None.__ne__, new_ids)) #drop nulls

        new_ids = pd.DataFrame(new_ids,columns=names)

        merged = new_ids.merge(df,how='left').reindex() #merge back with the old guy
        merged = clean(merged)
        return merged

class put(table):
    """put transformed dataframes into table"""
    def __init__(self,tablename):
        super().__init__(tablename)

    def replace(self,df,session,limit=200):
        table_obj = tables[self.tablename]
        rows = df.shape[0]
        print(f"insert or updating {rows} rows into {self.tablename}...")
        last = rows % limit
        sections = int((rows-last)/limit)
        pos = 0
        for i in range(sections):
            start=pos
            stop=pos+limit
            print(f"{start}-{stop}...")
            for i in range(start,stop):
                row = dict(df.iloc[i,:])
                session.merge(table_obj(**row))
            session.commit()
            print("...submitted.")
            time.sleep(1)
            pos += limit
        #last step
        start=pos
        stop=pos+last
        print(f"{start}-{stop}...")
        for i in range(pos,last):
            row = dict(df.iloc[i,:])
            session.merge(table_obj(**row))
        session.commit()
        print("...submitted.")
        print(f"submissions done. submitted: {stop} ")
        pass

"""df transformation helpers"""
def clean(df):
    t = df.drop_duplicates()
    t = df.replace('',np.nan)
    t = df.dropna(how='all')
    t = t.reindex()
    return t

def columns_from(df,colnames):
    df = df.where(pd.notnull(df),None).reindex() #change NaNs to Nones
    return df[colnames]

def add_column(df,constant,colname):
    df[colname]=constant
    return df

def rename_columns(df,left_ids,right_ids):
    dict_renames = dict(zip(left_ids,right_ids))
    return df.rename(columns=dict_renames)

def concat_tall(dflist):
    return pd.concat(dflist,axis=0).reindex()

def make_row(**kwargs):
    return pd.DataFrame([kwargs])

""" filters """
def users_table(df):
    colnames = table('users').colnames
    t = add_column(df,True,'is_user')
    t = columns_from(t,colnames)
    return t

def tracks_table(df):
    colnames = table('tracks').colnames
    t = add_column(df,False,'is_user')
    t = columns_from(t,colnames)
    return t

def manifest_table(df,ref_id_name,is_user,stamp_columns=[]):
    t = df[[ref_id_name]]
    t = rename_columns(t,[ref_id_name],['ref_id'])
    t['is_user']=is_user
    t = t[['ref_id','is_user']]
    if len(stamp_columns)>0:
        for i in stamp_columns:
            t[i] = int(time.time())
    return t

def favs_table(df,uid,is_user):
    colnames = table('favs').colnames
    if is_user == True:
        """ ie, Users.favorites.  user_id is imputed"""
        t = rename_columns(df,['id'],['track_id'])
        t['user_id']=uid
        return t[colnames]

    if is_user == False:
        """ ie, Tracks.favoriters.  track_id is imputed """
        t = rename_columns(df,['id'],['user_id'])
        t['track_id']=uid
        return t[colnames]
    else:
        return "error."

""" maps """
class favorites(object):
    """ fit df pulled from sc, along with uid reference.  transform to df format for tables"""
    def __init__(self,df,user_id): #fit
        self.df = df
        self.user_id = user_id

    def tracks(self):
        """ transform into tracks """
        return tracks_table(self.df)

    def favs(self):
        """ transform into favs """
        return favs_table(self.df, uid=self.user_id, is_user=True)

    def manifest(self):
        """stamp user favs as collected"""
        user = make_row(
            ref_id=self.user_id, is_user=True, favs=int(time.time())
            )

        """stamp tracks as collected"""
        fav_tracks = manifest_table(
            self.df,ref_id_name='id', is_user=False, stamp_columns=['tracks']
            )

        """identify artists to poll later"""
        fav_artists = manifest_table(
            self.df, ref_id_name='user_id', is_user=True, stamp_columns=[]
            )

        t = concat_tall([fav_tracks,fav_artists,user])
        return fav_tracks,fav_artists,user


class favoriters(object):
    """ fit df pulled from sc, along with uid reference.  transform to df format for tables"""
    def __init__(self,df,track_id): #fit
        self.df = df
        self.track_id = track_id

    def favs(self):
        """ transform into favs """
        return favs_table(self.df, uid=self.track_id, is_user=False)

    def manifest(self):
        """stamp track favs as collected"""
        track = make_row(
            ref_id=self.track_id, is_user=False, favs=int(time.time())
            )

        """identify users to poll later"""
        favoriters = manifest_table(
            self.df, ref_id_name='id', is_user=True, stamp_columns=[]
            )

        t = concat_tall([favoriters,track])
        return favoriters,track

class users:
    def __init__(self,df):
        self.df = df

    def users(self):
        return users_table(self.df)

    def manifest(self):
        """ mark users as collected """
        return manifest_table(self.df,ref_id_name='id',is_user=True,stamp_columns=['users'])

class tracks:
    def __init__(self,df):
        self.df = df

    def tracks(self):
        return tracks_table(self.df)

    def manifest(self):
        return manifest_table(self.df,ref_id_name='id',is_user=False,stamp_columns=['tracks'])
