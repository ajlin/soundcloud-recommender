from sqlalchemy.types import JSON, String, Integer, Boolean, Float, BigInteger
from sqlalchemy import create_engine,Table,MetaData,Column,text,ForeignKey
from psycopg2.extensions import register_adapter, AsIs
from psycopg2.extras import Json
import psycopg2.errorcodes
from sqlalchemy.exc import IntegrityError
import numpy as np
"""
settings.py

use:
import settings
from settings import

contents:


to do:
refactor
"""

""" Stuff Humans Can Change: """
#soundcloud api config
client_id = '1dff55bf515582dc759594dac5ba46e9'
pagination_limit = 200


#aws postgres db config
pg = dict(
    ip = '34.220.110.231',
    port = '5432',
    user = 'postgres',
    key = '3GXwojABHaEUDQ?jcr',
    sql = 'postgres',
    db = 'postgres'
)

#eg `postgres://admin:donotusethispassword@aws-us-east-1-portal.19.dblayer.com:15813/compose`
dbstring = "{sql}://{user}:{key}@{ip}:{port}/{db}".format(**pg)
engine_params = dict(
    pool_size = 15
    )


#sqlalchemy schema
#ForeignKey(['user_id','track_id'],[users.id,tracks.id])
users_cols = dict(
    id = {'type_': BigInteger, 'primary_key': True},
    kind = {'type_': String},
    permalink = {'type_': String},
    username = {'type_': String},
    last_modified = {'type_': String},
    uri = {'type_': String},
    permalink_url = {'type_': String},
    country = {'type_': String},
    first_name = {'type_': String},
    last_name = {'type_': String},
    full_name = {'type_': String},
    description = {'type_': String},
    city = {'type_': String},
    discogs_name = {'type_': String},
    website = {'type_': String},
    website_title = {'type_': String},
    track_count = {'type_': Integer},
    playlist_count = {'type_': Integer},
    plan = {'type_': String},
    public_favorites_count = {'type_': Integer},
    followers_count = {'type_': Integer},
    followings_count = {'type_': Integer},
    subscriptions = {'type_': JSON}
    )

tracks_cols = dict(
    id = {'type_':BigInteger, 'primary_key': True},
    comment_count = {'type_':Integer},
    commentable = {'type_':Boolean},
    created_at = {'type_':String},
    description = {'type_':String},
    download_count = {'type_':Integer},
    download_url = {'type_':String},
    downloadable = {'type_':Boolean},
    duration = {'type_':BigInteger},
    favoritings_count = {'type_':Integer},
    genre = {'type_':String},
    isrc = {'type_':String},
    kind = {'type_':String},
    label = {'type_':JSON},
    label_id = {'type_':Integer},
    label_name = {'type_':String},
    last_modified = {'type_':String},
    permalink = {'type_':String},
    permalink_url = {'type_':String},
    playback_count = {'type_':Integer},
    streamable = {'type_':Boolean},
    tag_list = {'type_':String},
    title = {'type_':String},
    track_type = {'type_':String},
    uri = {'type_':String},
    user = {'type_':JSON},
    user_id = {'type_':BigInteger}
    )

favs_cols = dict(
    user_id = {'type_':BigInteger, 'primary_key': True,},
    track_id = {'type_':BigInteger, 'primary_key': True},
    artist_id = {'type_':BigInteger, 'primary_key': True}
    )

coms_cols = dict(
    user_id = {'type_':BigInteger, 'primary_key': True},
    track_id = {'type_':BigInteger, 'primary_key': True},
    artist_id = {'type_':BigInteger, 'primary_key': True}
    )

manifest_cols = dict(
    id_type = {'type_':Boolean, 'primary_key': True},
    uid = {'type_':BigInteger, 'primary_key': True},
    last_collected = {'type_':String}
    )


"""
#users table
users_cols = {'id':{'type_':BigInteger,'primary_key':True},
              'kind':{'type_':String},
              'permalink':{'type_':String},
              'username':{'type_':String},
              'last_modified':{'type_':String},
              'uri':{'type_':String},
              'permalink_url':{'type_':String},
              'country':{'type_':String},
              'first_name':{'type_':String},
              'last_name':{'type_':String},
              'full_name':{'type_':String},
              'description':{'type_':String},
              'city':{'type_':String},
              'discogs_name':{'type_':String},
              'website':{'type_':String},
              'website_title':{'type_':String},
              'track_count':{'type_':Integer},
              'playlist_count':{'type_':Integer},
              'plan':{'type_':String},
              'public_favorites_count':{'type_':Integer},
              'followers_count':{'type_':Integer},
              'followings_count':{'type_':Integer},
              'subscriptions':{'type_':JSON}}

# tracks table


tracks_cols = {'id':{'type_':BigInteger,'primary_key':True},
               'comment_count':{'type_':Integer},
               'commentable':{'type_':Boolean},
               'created_at':{'type_':String},
               'description':{'type_':String},
               'download_count':{'type_':Integer},
               'download_url':{'type_':String},
               'download_url':{'type_':String},
               'downloadable':{'type_':Boolean},
               'duration':{'type_':BigInteger},
               'favoritings_count':{'type_':Integer},
               'genre':{'type_':String},
               'isrc':{'type_':String},
               'kind':{'type_':String},
               'label':{'type_':JSON},
               'label_id':{'type_':Integer},
               'label_name':{'type_':String},
               'last_modified':{'type_':String},
               'permalink':{'type_':String},
               'permalink_url':{'type_':String},
               'playback_count':{'type_':Integer},
               'streamable':{'type_':Boolean},
               'tag_list':{'type_':String},
               'title':{'type_':String},
               'track_type':{'type_':String},
               'uri':{'type_':String},
               'user':{'type_':JSON},
               'user_id':{'type_':BigInteger}
               }

for i in tracks_cols:
    print(f"{i},{tracks_cols[i]}")


for key in users_cols:
    string = f"{key}=Column("
    for k in users_cols[key]:
        string += f"{k}={users_cols[key][k]},"
    string = string[0:-1]
    string += ')'
    print(string)

"""

"""sqlalchemy engine"""
engine = create_engine(dbstring,)

"""table definitions for sqlalchemy to make writing to our tables cleaner/safer"""

tables = {'tracks':tracks_cols,
          'users':users_cols,
          'favs':favs_cols,
          'coms':coms_cols,
          'manifest':manifest_cols}

def buildschema(engine,table_dict):
    meta = MetaData(engine)
    for i in table_dict:
        Table(i,meta,*[Column(key,**table_dict[i][key]) for key in table_dict[i]])
    return meta

meta = buildschema(engine,tables)

"""psycopg2 / postgresql type handling"""
register_adapter(dict,lambda py_dict: Json(py_dict))
register_adapter(np.int64, lambda np_int64: AsIs(np_int64))
