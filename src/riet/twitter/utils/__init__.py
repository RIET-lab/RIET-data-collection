import datetime as dt
from rfc3339 import rfc3339
import json
import os
import tweepy
import time
import logging

# Global defaults
VERSION = '2'
PREFIX = 'https://api.twitter.com'
MAX_RESULTS = 100 # API Max by default
TWEET_FIELDS = 'id,author_id,conversation_id,referenced_tweets,created_at'

logger = logging.getLogger(__name__)

#########################################################
########### handling / formatting / creds ###############
#########################################################

def get_time(*args):
    """returns time in iso8601 for twitter API
    arg order: y,m,d,h*,m*,s*,us* *=optional 
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
########### API helpers #################################
#########################################################

def tweepy_loop(twitter_fn, search_params={}, verbose=False, max_steps=None):
    """Runs a tweepy paginated loop
    Args:
        twitter_fn: tweepy call fn
        search_params: params to add to fn
        verbose: whether to print meta of results
        max_steps: limit # of calls
    Returns:
        Unstructured results
    """
    data = []
    cnt = 0
    for response in tweepy.Paginator(twitter_fn, **search_params):
        cnt += 1
        data.extend(response.data)
        if verbose: logger.info(json.dumps(response.meta))
        if max_steps and cnt >= max_steps: break
        if response.meta.get('next_token'): time.sleep(1)
    
    return data

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
    data = []
        
    for response in tweepy.Paginator(twitter_call, **search_params):
        data.extend(response.data)
        if verbose: logger.info(json.dumps(response.meta))
        if response.meta.get('next_token'): time.sleep(1)
    
    if get_root:
        root_response = client.get_tweet(conversation_id, tweet_fields=search_params["tweet_fields"])
        data = [root_response.data] + data
    
    return data
    
    
def run_query(client,
              query,
              params={},
              search_all=True,
              verbose=False,
              max_steps=10000):
    """
    Runs a query to get all results
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
        query=query,
        tweet_fields=TWEET_FIELDS,
        max_results=MAX_RESULTS
    )
    search_params.update(params)
    twitter_call = client.search_all_tweets if search_all else client.search_recent_tweets
    data = []
    
    cnt = 0
    for response in tweepy.Paginator(twitter_call, **search_params):
        cnt += 1
        data.extend(response.data)
        if verbose: logger.info(json.dumps(response.meta))
        if cnt >= max_steps: break
        if response.meta.get('next_token'): time.sleep(1)
    
    return data