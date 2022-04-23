import boto3
import json
import tweepy

SECRET_NAMES = dict(
    mes21010 = "TwitterAPICredential-mes21010",
    shiridh = "TwitterAPICredential-shiridh"
)

def get_secret(aws_credentials, credentials_user):
    secret_name = SECRET_NAMES[credentials_user]
    region_name = "us-east-1"

    client = boto3.client('secretsmanager',
                          aws_access_key_id=aws_credentials.get("AWS_ACCESS_KEY_ID"),
                          aws_secret_access_key=aws_credentials.get("AWS_SECRET_ACCESS_KEY"), #secret_access_key,
                          region_name=region_name
    )

    secret = client.get_secret_value(SecretId=secret_name)
    return json.loads(secret["SecretString"])

def get_twitter_credentials(aws_credentials, credentials_user):
    secret = get_secret(aws_credentials, credentials_user)
    return dict(
        bearer_token=secret.get("BEARER_TOKEN"),
        consumer_key=secret.get("KEY"),
        consumer_secret=secret.get("SECRET_KEY"),
        access_token=secret.get("ACCESS_TOKEN"),
        access_token_secret=secret.get("ACCESS_TOKEN_SECRET")
    )

def get_tweepy_api(aws_credentials, credentials_user, **kwargs):
    auth = get_twitter_credentials(aws_credentials, credentials_user)
    tweepy_auth = tweepy.OAuthHandler(auth.get("consumer_key"), auth.get("consumer_secret"))
    tweepy_auth.set_access_token(auth.get("access_token"), auth.get("access_token_secret"))
    return tweepy.API(tweepy_auth, **kwargs)

def get_tweepy_client(aws_credentials, credentials_user="mes21010", **kwargs):
    auth = get_twitter_credentials(aws_credentials, credentials_user)
    return tweepy.Client(**auth, **kwargs)