import datetime as dt
from rfc3339 import rfc3339
import json
import os
import tweepy

# Global defaults
VERSION = '2'
PREFIX = 'https://api.twitter.com'
MAX_RESULTS = 500 # API Max
TWEET_FIELDS = 'id,author_id,conversation_id,referenced_tweets,created_at'

#########################################################
########### handling / formatting / creds ###############
#########################################################

def get_time(*args):
    """
    returns time in iso8601 for twitter API
    """
    date = dt.datetime(*args)
    return rfc3339(date)


def get_twitter_url(tweet_id):
    return f'https://twitter.com/twitter/statuses/{tweet_id}'


def get_url(endpoint, version=VERSION, prefix=PREFIX):
    return os.path.join(prefix, version, endpoint)

def get_credentials():
    return dict(
        bearer_token=os.environ.get("TWITTER_BEARER_TOKEN"), 
        consumer_key=os.environ.get("TWITTER_CONSUMER_KEY"), 
        consumer_secret=os.environ.get("TWITTER_CONSUMER_SECRET"), 
        access_token=os.environ.get("TWITTER_ACCESS_TOKEN"), 
        access_token_secret=os.environ.get("TWITTER_TOKEN_SECRET")
    )

#########################################################
########### helper classes for structure ################
#########################################################

class placeholder_tweet:
    text = ""
    author_id = ""
    created_at = None
    is_placeholder = True

    def __init__(self, node_id):
        self.id = node_id

class TweetNode:
    """
    Class to handle tweets
    """
    def __init__(self, tweet):
        self.tweet = tweet
        self.parents = set()
        self.children = set()
        
    def add_parent(self, parent):
        self.parents.add(parent)
        
    def add_child(self, child):
        self.children.add(child)
        
    def is_placeholder(self):
        return hasattr(self.tweet, "is_placeholder")
        
    def __hash__(self):
        return self.tweet.id
    
    def __str__(self):
        return self.convert_tweet_to_string(self.tweet)
        
    @classmethod
    def placeholder(cls, node_id):
        return cls(placeholder_tweet(node_id))
    
    @staticmethod
    def convert_tweet_to_string(tweet):
        tweet_dic = dict(
            author = tweet.author_id,
            text = tweet.text,
            created_at = tweet.created_at
        )
        return json.dumps(tweet_dic)
    
class TweetTree:
    """
    Class to handle tweet tree
    """
    nodes = {}
    
    def __init__(self, root):
        self.root = root
        
    def __getitem__(self, node_id):
        return nodes.get(node_id)
    
    @classmethod
    def from_node(cls, client, node, is_root=False):
        """
        Will make API calls to generate tree from single node
        """
        self.from_conversation_id(client, 
                                  node.tweet.conversation_id, 
                                  node if is_root else None)
    
    @classmethod
    def from_conversation_id(cls, client, conversation_id, root=None):
        """
        Will make API calls to generate tree from conversation id
        """
        tweets = get_conversation(client, conversation_id, get_root=root is None)
        tweets = [TweetNode(tweet) for tweet in tweets]
        tree = cls(tweets[0])
        tree.nodes = cls.fill_in_nodes(tweets)
        return tree
        
    @staticmethod
    def fill_in_nodes(nodes):
        node_dict = {}
        for node in nodes: node_dict[hash(node)] = node
        
        for node in nodes:
            parents = node.tweet.referenced_tweets or []
            for parent in parents:
                parent_node = node_dict.get(parent.id, TweetNode.placeholder(parent.id))
                parent_node.add_child(node)
                node.add_parent(parent_node)
                
        return node_dict
    
#########################################################
########### API helpers #################################
#########################################################

def get_conversation(client,
                     conversation_id,
                     params={},
                     search_all=True,
                     get_root=True,
                     verbose=False):
    """
    Returns conversation
    Args:
        client: tweepy Client
        conversation_id: string of twitter conv id
        search_params: params to update default
        search_all: bool recent vs all twitter api
        get_root: bool of whether to return root node as well
        verbose: Log statements while running
    Returns:
        unstructured tweets
        
    """
    search_params = dict(
        query=f'conversation_id:{conversation_id}',
        tweet_fields=TWEET_FIELDS,
        max_results=MAX_RESULTS
    )
    search_params.update(params)
    twitter_call = client.search_all_tweets if search_all else client.search_recent_tweets
    response = twitter_call(**search_params)
    data = response.data    
    
    if get_root:
        root_response = client.get_tweet(conversation_id, tweet_fields=search_params["tweet_fields"])
        data = [root_response.data] + data
    
    return data
    
    
        
    
        