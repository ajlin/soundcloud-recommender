from data_utils import sc,aws
import pandas as pd, numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import time
import datetime
#alex's user_id:  743108

def build_pivot(engine,filter_limit=2):
    """nb: set filter limit at 2 in order to significantly reduce the 'under'-crawled, mostly-sparse columns of users and items."""
    master_favs = pd.read_sql('favs',engine)
    limt = filter_limit
    print("unique interactions from db: ", master_favs.shape[0])
    track_users = master_favs.groupby('track_id').count()
    user_tracks = master_favs.groupby('user_id').count()
    print("unique users:",user_tracks.shape[0])
    print("unique tracks:",track_users.shape[0])

    #now we filter
    track_filter = master_favs['track_id'].isin(track_users[track_users['user_id']>limit].index)
    user_filter = master_favs['user_id'].isin(user_tracks[user_tracks['track_id']>limit].index)
    filtered = master_favs[track_filter][user_filter]
    filtered['interaction'] = 1 #add interaction term

    print("filtered interactions: ",filtered.shape[0])
    track_users = filtered.groupby('track_id').count()
    user_tracks = filtered.groupby('user_id').count()
    print("filtered users:",user_tracks.shape[0])
    print("filtered tracks:",track_users.shape[0])
    pivot = pd.pivot_table(filtered,values='interaction',index='track_id',columns='user_id').fillna(0)
    now = datetime.datetime.utcfromtimestamp(time.time()).strftime('%Y_%m_%d__%H_%M_00_utc')
    pivot.to_pickle(f"./model/pivot.pkl")

def build_cosim(engine):
    pivot = pd.read_pickle("./model/pivot.pkl")
    users = pivot
    tracks = pivot.T
    tracks_cosim = cosine_similarity(users)
    item_item = pd.DataFrame(tracks_cosim ,index=tracks.columns,columns=tracks.columns)
    item_item.to_pickle(f"./model/item_item.pkl")

    users_cosim = cosine_similarity(tracks)
    user_user = pd.DataFrame(users_cosim,index=users.columns,columns=users.columns)
    user_user.to_pickle(f"./model/user_user.pkl")

def __main__():
    engine = aws.schema.myengine
    build_pivot(engine)
    build_cosim(engine)

__main__()
