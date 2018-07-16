import data_utils.settings
import requests
import pandas as pd
import time

from data_utils.settings import client_id
from data_utils.settings import pagination_limit as limit


#########################
api_url = 'https://api.soundcloud.com/' #base url for api endpoints

headers = {'client_id':client_id, #application access key
            'order':'created_at',
            'limit':limit,
            'linked_partitioning':1} #SC's api settings for pagination
#########################

#for working around soundcloud api

class api(object):
    """ just for keeping the soundcloud api requests straight when feeding into a Requests item """
    def __init__(self,base,api):
        self.api_,self.base_ = api,base.copy()
        #######################
        self.url = None
        self.params = headers.copy()
        return None

    def param(self,*args,**kwargs):
        url = self.api_

        for i in range(len(args)):
            if i<=2: # first three are dirs 'https://api/endpoint/id/subordinate/'
                url += str(args[i])+'/'
            else: # everything else is a param
                self.params.update(args[i])
            self.params.update(kwargs)
        self.url = url
        return self

    def get(self,paginate=False,steps=55):
        """ paginate through API requests... note: default max steps is set to 55, or about 11k users/tracks.
        any more is beyond my abilities or capacity to optimize right now (only gathering full data on about 300/day or so)
        and so i've decided, out of my scope to handle for now."""
        if paginate is True:
            url = self.url
            post_ = []
            count_ = 0
            for _ in range(steps): #page limit not really a factor for our scraper so far
                if url == None:
                    print('done. output length: ',len(post_))
                    break
                else:
                    res = requests.get(url=url,params=self.params)
                    try:
                        res.raise_for_status() #check status
                    except requests.HTTPError: #wait a smidge longer for status
                        time.sleep(.1)

                    if res.status_code == 200:
                        json = res.json()['collection']
                        post_.extend(json)
                        count_ += 1
                        print('step ',count_,'; length ',len(post_))
                        try:
                            url = res.json()['next_href']
                        except KeyError:
                            url=None
                    elif res.status_code != 200:
                        print('error status code: ', res.status_code)
                        print('at step: ',count_)
                        print('url: ',str(url[12:36]+'...'))
                        break #if bad page, move on
            time.sleep(1) #for the thing
            return post_
        elif paginate is False:
            return requests.get(url=self.url,params=self.params).json()


class base:
    def __init__(self,end):
        self.end = end

    def multi(self,*args,**kwargs):
        soundcloud = api(base=headers.copy(),api=api_url)
        soundcloud.param(self.end,*args,**kwargs)
        df = pd.DataFrame(soundcloud.get(paginate=True))
        return df

    def single(self,uid,*args): #same as multi, just assumes a single ID and no paginate
        soundcloud = api(base=headers.copy(),api=api_url)
        soundcloud.param(self.end,uid,*args)
        return soundcloud.get()

    def bulk(self,list_ids):
        #limit global from above
        count = len(list_ids)
        last = count % limit
        pos=0
        output = pd.DataFrame()
        for i in range(int((count-last)/limit)):
            ids = ','.join(str(x) for x in list_ids[pos:pos+limit]) #parse the list for soundcloud's API filter
            r = self.multi(ids=ids,limit=limit)
            output = pd.concat([output,r],axis=0,ignore_index=True).drop_duplicates(['id'])
            pos+=limit
        #last step
        ids = ','.join(str(x) for x in list_ids[pos:pos+last])
        r = self.multi(ids=ids,limit=limit)
        output = pd.concat([output,r],axis=0,ignore_index=True).drop_duplicates(['id'])
        return output

class Resolve:
    def resolve(url,client_id='1dff55bf515582dc759594dac5ba46e9',**kwargs): #get API response out of a public URL
        endpoint = 'https://api.soundcloud.com/resolve'
        params = {'client_id':client_id} #api key
        params['url'] = url #endpoint
        params.update(kwargs) #in case there are other kwargs you want to feed into params

        res = requests.get(endpoint,params=params)
        res.raise_for_status()
        return res.json()

    def user_id(username): #get UID from a public username
        url = 'http://soundcloud.com/'+username
        return self.resolve(url)['id']

class Users:
    def user(user_id):
        return base('users').single(user_id)

    def users(user_ids):
        return base('users').bulk(user_ids)

    def tracks(user_id):
        return base('users').multi(user_id,'tracks')

    def favorites(user_id):
        return base('users').multi(user_id,'favorites')

    def comments(user_id):
        return base('users').multi(user_id,'comments')

class Tracks:
    def track(track_id):
        return base('tracks').single(track_id)

    def tracks(track_ids):
        return base('tracks').bulk(track_ids)

    def favoriters(track_id): #list favoriters
        return base('tracks').multi(track_id,'favoriters')

    def comments(track_id):
        return base('tracks').multi(track_id,'comments')
