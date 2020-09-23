"""
A script to grab economists on Twitter using the Tweepy API, and save them to the dataset econs.csv.
"""

#--------------IMPORTS-----------------

import tweepy
import pandas as pd
import numpy as np

#-------------SET UP TWEEPY--------------

# import API keys, private
keys = pd.read_csv("api.csv")
keys = dict(zip(list(keys.columns), list(keys.iloc[0,])))

# make an AppAuth API for faster rates
auth = tweepy.AppAuthHandler(keys['key'], keys['secret'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#-------------GET REPEC ECONOMISTS---------------

# Use tweepy to scrape the RePEc Twitter list, found at https://twitter.com/i/lists/1087053821786947584
lst = []
repec = tweepy.Cursor(api.list_members, list_id=1087053821786947584).items()
for user in repec:
    l = [user.name, user.screen_name, user.id_str, user.friend_count, user.followers_count, user.verified, user.favourites_count, 
         user.created_at, user]
    lst.append(l)

cols = ['name', 'handle', 'id', 'following', 'followers', 'verified', 'favorites', 'join_date', 'object']
repec = pd.DataFrame(lst, columns = cols)
print(repec.info())

#-------------GET ECONOMISTS FROM TWEETS DIRECTLY-----------------

# Supplement the RePEc dataset with people who tweeted on #EconTwitter twice in the last 30 days (grabbed on September 14th, 2020)
ect = tweepy.Cursor(api.search, q = "#econtwitter").items(10000)
repecs = list(repec.handle)

lst = []
dct = {}
for tweet in ect:
    auth = tweet.author    
    if auth.screen_name in dct.keys():
        dct[auth.screen_name] = True
    else:
        dct[auth.screen_name] = False
    if auth.screen_name not in repecs and dct[auth.screen_name]:
        repecs.append(auth.screen_name)
        l = [auth.name, auth.screen_name, auth.id_str, auth.friends_count, auth.followers_count, auth.verified, 
             auth.favourites_count, auth.created_at, auth]
        lst.append(l)
    
supp = pd.DataFrame(lst, columns = cols)

# identify the humans vs bots/institutional accounts through naming proxies
keywords = ["economics", "econometrics", "bot", "economists", "microeconomics", "economic", "center", "centre", "university"]
def check_human(name):
    l = [word in name.lower() for word in keywords]
    return(not (True in l))
supp.is_human = supp.name.map(check_human)

#-----------------MERGE AND SAVE-------------------

econs = pd.concat([repec, supp])
econs.dropna(inplace=True)
econs.join_date = pd.to_datetime(econs.join_date)
econs.set_index("id", inplace=T)
econs.to_pickle("econs.pkl") # preserves the user objects so they can be referenced later
econs.to_csv("econs.csv") # write to shareable format