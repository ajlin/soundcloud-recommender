import pandas as pd,numpy as np
from data_utils import sc,aws

class cosim(object):
    def __init__(self,is_user=True,uid=743108):
        self.uid = uid
        self.is_user = is_user
        self.n_filter = None #number of top/bottom similar items/users to filter by
        self.bot_alike = None
        self.top_alike = None
        self.weights = None
        self.vector = None
        self.suggestions = None
        self.similar = None
        self.tcols = "title tag_list permalink_url stream_url id genre duration created_at user_id".split()
        self.ucols = "username city country permalink_url track_count followers_count followings_count public_favorites_count id".split()

        if is_user == True:
            self.get = sc.Tracks.tracks
            self.get_alike = sc.Users.users
            self.cols = self.tcols
            self.acols = self.ucols
        if is_user == False:
            self.get = sc.Users.users
            self.get_alike = sc.Tracks.tracks
            self.cols = self.ucols
            self.acols = self.tcols

        self.fit()


    def fit(self):
        self.user_user = pd.read_pickle("./model/user_user.pkl")
        self.item_item = pd.read_pickle("./model/item_item.pkl")
        #if already in table:
        if self.is_user is True:
            self.pivot = pd.read_pickle('./model/pivot.pkl')
            self.similar = self.user_user[self.uid].drop(self.uid)
        if self.is_user is False:
            self.pivot = pd.read_pickle('./model/pivot.pkl').T
            self.similar = self.item_item[self.uid].drop(self.uid)

        self.similar = self.similar.sort_values(ascending=False)
        self.vector = self.pivot[self.uid]
        return self

    def suggest(self,n=20,top=True):
        assert type(top) == bool
        self.weights = self.similar.values/np.sum(self.similar.values)
        no_interaction = self.pivot[self.vector==0]
        no_interaction = no_interaction.drop(self.uid,axis=1)
        no_interaction = no_interaction[self.similar.index]
        suggestions = np.dot(no_interaction.fillna(0).values,self.weights)
        suggestions = pd.DataFrame(suggestions,index=no_interaction.index)[0].sort_values(ascending=False)
        self.suggestions = suggestions
        if top is True:
            return self.get(suggestions.head(n).index)[self.cols]
        if top is False:
            return self.get(suggestions.tail(n).index)[self.cols]
        return 'error'

    def alike(self,n=20,top=True):
        assert type(top)==bool
        if top is True:
            return self.get_alike(self.similar.head(n).index)[self.acols]
        if top == False:
            return self.get_alike(self.similar.tail(n).index)[self.acols]
        return "error"
