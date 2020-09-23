"""
A script to build the EconTwitter graph from the nodes collected in get_econs.py.
"""

#--------------IMPORTS----------------

import pandas as pd
import networkx as nx
import tweepy 

#-------------SET UP TWEEPY--------------

# import API keys, private
keys = pd.read_csv("api.csv")
keys = dict(zip(list(keys.columns), list(keys.iloc[0,])))

# AppAuth for fast rates
auth = tweepy.AppAuthHandler(keys['key'], keys['secret'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# OAuth if we need it
oauth = tweepy.OAuthHandler(keys['key'], keys['secret'])
oauth.set_access_token(keys['token'], keys['token_sec'])
oapi = tweepy.API(oauth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#--------------BUILD NETWORK-----------------

# load data
econs = pd.read_pickle("econs.pkl")
econs.set_index("id", inplace=True)

# make graph with nodelist and node attributes
G = nx.DiGraph() 
G.add_nodes_from(list(econs.index))
cols = list(econs.columns)
cols.remove("object")
for col in cols:
   nx.set_node_attributes(G, pd.Series(econs[col]).to_dict(), col)

# add edges by iterating through friend lists 
# this step takes a LONG TIME - 15 minutes per 15 users rate limit --> 38 hours required to fill 2285 users
ids = list(econs.index)
failed = []
j = 0
for i in ids:
    j += 1
    print(str(i) + " " + str(j))
    try:
        following = list(api.friends_ids(user_id = i))
        econ_follows = list(set(ids) & set(following))
        joined = list(zip([i] * len(econ_follows), econ_follows))
        G.add_edges_from(joined)
        nx.write_gpickle(G, "econtwitter.gpickle")
    except tweepy.error.TweepError as ex:
        print(ex.reason)
        failed.append(i)

# second round to get any that were missed due to internet connection issues 
# if they were missed due to protected account, this will have no effect
for i in failed:
    try:
        following = list(api.friends_ids(user_id = i))
        econ_follows = list(set(ids) & set(following))
        joined = list(zip([i] * len(econ_follows), econ_follows))
        G.add_edges_from(joined)
        nx.write_gpickle(G, "econtwitter.gpickle")
    except tweepy.error.TweepError as ex:
        print(ex.reason) # should only be "Not authorized"

#----------------AUGMENT NODELIST WITH NETWORK INFO------------------

econs.reset_index(inplace = True)
econs['econ_following'] = econs.id.map(G.out_degree)
econs['econ_followers'] = econs.id.map(G.in_degree)
econs['following_ratio'] = econs['econ_following']/econs['following']
econs['followers_ratio'] = econs['econ_followers']/econs['followers']

# get centrality information 
in_dict = nx.in_degree_centrality(G) 
in_df = pd.DataFrame(list(in_dict.items()), columns = ['id', 'in_deg_centrality'])
out_dict = nx.out_degree_centrality(G) 
out_df = pd.DataFrame(list(out_dict.items()), columns = ['id', 'out_deg_centrality'])
cent_df = in_df.merge(out_df, on = "id")
econs = econs.merge(cent_df, on = "id")

# get average neighborhood degree 
nbhd_dict = nx.average_neighbor_degree(G, source='out', target='in')
nbhd_df = pd.DataFrame(list(nbhd_dict.items()), columns = ['id', 'avg_followers_of_following'])
econs = econs.merge(nbhd_df, on = "id")

#----------------SAVE NETWORK TO CSV------------------

# save nodelist
econs.to_csv("econs.csv", index = False)

# save edgelist 
edge_df = nx.to_pandas_edgelist(G)
edge_df.to_csv("econs_edges.csv", index = False) 
