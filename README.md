# EconTwitter Network

EconTwitter is one of my favorite communities on the internet---a place to find new papers as well as new recipes. So I thought it would be fun to create the EconTwitter network that represents this community, so that anyone can examine what it really looks like.

### econs.csv

This is the universe of Twitter economists. Of course, the boundaries defining an "economist" are hard to define. I created this dataset from two sources:

1. The RePEc [list](https://ideas.repec.org/i/etwitter.html) of economists on Twitter.
   - This represents the largest official list of economists on Twitter that I could find
2. Repeated #EconTwitter tweeters.
   - I defined this as anyone who tweeted with the hashtag #EconTwitter more than twice in the 30-day period before September 14th, 2020 (when I created the dataset).
   - This consists of both RePEc economists and people who are active on EconTwitter even if not officially listed (e.g. because they are predocs/PhD students/working in industry)  

When building the EconTwitter network, this is the node list.

The variables in `econs.csv` are:

|          Variable          |                             Meaning                            |
|:--------------------------:|:--------------------------------------------------------------:|
|             id             |                     The user's numerical ID                    |
|            name            |                     The user's display name                    |
|           handle           |                       The user's @ handle                      |
|          following         |              How many people does the user follow?             |
|          followers         |                How many people follow the user?                |
|          verified          |                      Is the user verified?                     |
|          favorites         |             How many tweets has the user favorited?            |
|          join_date         |                 When did the user join Twitter?                |
|           object           | A Python stringified object representing other user attributes |
|          is_human          |       Is the user human, or a bot/institutional account?       |
|       econ_following       |            How many economists does the user follow?           |
|       econ_followers       |              How many economists follow the user?              |
|       following_ratio      |       What fraction of the user's follows are economists?      |
|       followers_ratio      |      What fraction of the user's followers are economists?     |
|      in_deg_centrality     |     What is the user's in-degree centrality in the network?    |
|     out_deg_centrality     |    What is the user's out-degree centrality in the network?    |
| avg_followers_of_following |    How many followers do the user's follows have on average?   |

### econtwitter.gpickle

This is a pickled file, readable only in Python using NetworkX. It is a directed graph representing the EconTwitter network. I built this network iteratively from the `econs.csv` node list. The generation process is straightforward: search through the follow-list of every node, and create an edge from X to Y if Y is in both X's follow-list and in the node list.

### econs_edges.csv

This is an edge list for the EconTwitter network, created indirectly from `econtwitter.gpickle`. It simply saves every source-target pair in the network, so that the network can be recreated outside of Python.
