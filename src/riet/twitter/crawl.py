"""
Script to crawl the latest tweets of known misinformation spreaders on Twitter.
"""
from tweepy import Client
from tweepy.pagination import Paginator
from tweet import Tweet
import dotenv
import boto3
import json
import os
import time

from tweet import TweetEncoder

FILE_NAME = "data.json"
MAX_RESULTS = 10
TWEET_FIELDS = [
    "id",
    "author_id",
    "text",
    "conversation_id",
    "created_at",
    "referenced_tweets",
]
MISINFO_SPREADRES = [
    "ChildrensHD",
    "RobertKennedyJr",
    "realFFK",
    "IngrahamAngle",
    "TuckerCarlson",
    "drscottjensen",
    "AlexBerenson",
    "gbdeclaration",
    "laralogan",
    "MattWalshBlog",
    "SharylAttkisson",
    "delbigtree",
    "HighWireTalk",
    "DonaldJTrumpJr",
    "drsimonegold"
    "JennaEllisEsq"
    "vaxxed2",
    "unhealthytruth",
    "mercola",
    "detoxprofessor",
    "DrButtar",
    "sayerjigmi"
    "KellyBroganMD"
    "drchrisnorthrup",
    "dbongino"
]


def get_secret() -> dict:
    dotenv.load_dotenv()
    secret_name = "TwitterAPICredential-mes21010"
    region_name = "us-east-1"
    access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    client = boto3.client('secretsmanager',
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key,
                          region_name=region_name)
    secret = client.get_secret_value(SecretId=secret_name)

    return json.loads(secret["SecretString"])


def get_auth() -> dict:
    secret = get_secret()
    return dict(bearer_token=secret.get("BEARER_TOKEN"),
                consumer_key=secret.get("KEY"),
                consumer_secret=secret.get("SECRET_KEY"),
                access_token=secret.get("ACCESS_TOKEN"),
                access_token_secret=secret.get("ACCESS_TOKEN_SECRET"))


def reconstruct_conversation(tweets: dict[str, Tweet]) -> Tweet:
    """
    Reconstruct the conversation tree given all the tweets involved.
    """
    root = None

    for node in tweets.values():
        references = node["referenced_tweets"] if node["referenced_tweets"] is not None else []

        # Set parent to "replied_to" id
        for reference in references:
            if reference["type"] == "replied_to":
                parent = tweets[reference["id"]]
                node.parent = parent
                parent.replies.add(node)

        # If the node doesn't have a parent, it must be the root
        if node.parent == None:
            root = node

    return root


def main() -> None:
    data = []
    client = Client(**get_auth(), wait_on_rate_limit=True)

    for user in MISINFO_SPREADRES:
        query = f"from:{user} -is:retweet -is:reply"
        print(f"Querying tweets from {user}...")

        # Fetch latest tweets from `user`
        for tweet_page in Paginator(client.search_all_tweets,
                                    query,
                                    tweet_fields=TWEET_FIELDS,
                                    max_results=MAX_RESULTS):

            for root_tweet in tweet_page.data:
                tweets = {}

                # root = Tweet(root_tweet)
                tweets[root_tweet.id] = Tweet(root_tweet)
                # print(json.dumps(root, indent=4, cls=TweetEncoder))

                # Fetch all the tweets that replied to the original
                for conversation_page in Paginator(client.search_all_tweets,
                                                   f"conversation_id:{root_tweet.conversation_id}",
                                                   tweet_fields=TWEET_FIELDS,
                                                   max_results=MAX_RESULTS):
                    # Add replies to a dictionary of tweets
                    for tweet in conversation_page.data:
                        # tweet_obj = Tweet(tweet)
                        tweets[tweet.id] = Tweet(tweet)
                        # print(json.dumps(tweet_obj, indent=4, cls=TweetEncoder))

                    # Sleep before fetching next page
                    if "next_token" in conversation_page.meta:
                        time.sleep(5)

                conversation = reconstruct_conversation(tweets)

                if conversation is None:
                    print(f"Failed to reconstruct tree of Tweet {root_tweet.id}")
                else:
                    data.append(conversation)
                    print(json.dumps(conversation, indent=4, cls=TweetEncoder))

    # Write data to file
    with open(FILE_NAME, "w") as file:
        json.dump(data, file, indent=4, cls=TweetEncoder)
    print(f"Saved {len(data)} posts to {FILE_NAME}")


if __name__ == "__main__":
    # test_reconstruct_conversation()
    main()
