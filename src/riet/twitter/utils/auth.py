import boto3
import json
import tweepy

def get_secret(aws_credentials):
    secret_name = "TwitterAPICredential-mes21010"
    region_name = "us-east-1"

    client = boto3.client('secretsmanager',
                          aws_access_key_id=aws_credentials.get("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=aws_credentials.get("AWS_SECRET_ACCESS_KEY"), #secret_access_key,
                          region_name=region_name
    )

    secret = client.get_secret_value(SecretId=secret_name)
    return json.loads(secret["SecretString"])

def get_twitter_credentials(aws_credentials):
    secret = get_secret(aws_credentials)
    return dict(
        bearer_token=secret.get("BEARER_TOKEN"),
        consumer_key=secret.get("KEY"),
        consumer_secret=secret.get("SECRET_KEY"),
        access_token=secret.get("ACCESS_TOKEN"),
        access_token_secret=secret.get("ACCESS_TOKEN_SECRET")
    )

def get_tweepy_api(aws_credentials, **kwargs):
    auth = get_twitter_credentials(aws_credentials)
    tweepy_auth = tweepy.OAuthHandler(auth.get("consumer_key"), auth.get("consumer_secret"))
    tweepy_auth.set_access_token(auth.get("access_token"), auth.get("access_token_secret"))
    return tweepy.API(tweepy_auth, **kwargs)

def get_tweepy_client(aws_credentials, **kwargs):
    auth = get_twitter_credentials(aws_credentials)
    return tweepy.Client(**auth, **kwargs)