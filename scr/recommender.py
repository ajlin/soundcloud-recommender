import pandas as pd
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
        self.tcols = "title tag_list permalink_url stream_url id genre duration created_at user_id".split()
        self.ucols = "username city country permalink_url track_count followers_count followings_count public_favorites_count id".split()

        if is_user == True:
            self.get = sc.Tracks.tracks
            self.cols = self.tcols
        if is_user == False:
            self.get = sc.Users.users
            self.cols = self.ucols

        self.fit()


    def fit(self):
        self.user_user = pd.read_pickle("./model/user_user.pkl")
        self.item_item = pd.read_pickle("./model/item_item.pkl")
        #if already in table:
        if self.is_user == True:
            self.pivot = pd.read_pickle('./model/pivot.pkl')
            self.similar = self.user_user[self.uid].drop(uid)
        if self.is_user == False:
            self.pivot = pd.read_pickle('./model/pivot.pkl').T
            self.similar = self.item_item[self.uid].drop(uid)

        self.similar = self.similar.sort_values(ascending=False)
        self.vector = self.pivot[self.uid]
        return self

    def suggest(n=20,filter=False,n_filter=10):
        self.n_filter = n_filter
        self.bot_alike = self.similar.tail(n_filter).index
        self.top_alike = self.similar.head(n_filter).index
        self.weights = self.similar.values/np.sum(self.similar.values)
        no_interaction = self.pivot[self.vector==0]
        no_interaction = no_interaction.drop(self.uid,axis=1)
        no_interaction = no_interaction[self.similar.index]
        suggestions = np.dot(no_interaction.fillna(0).values,weights)
        suggestions = pd.DataFrame(suggestions,index=no_interaction.index)[0].sort_values(ascending=False)
        self.suggestions = suggestions
        return self.get(suggestions.head(20).index)[cols]
