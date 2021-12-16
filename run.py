from riet.twitter.streams import hourlyStream
from riet.twitter.utils import auth
import argparse
import os

parser = argparse.ArgumentParser(description='run a twitter stream')
parser.add_argument('--rootdir', type=str, default=".",
                    help='root directory of stream collection')
parser.add_argument('--track', type=str, nargs='+', default=[],
                    help='keywords to track')
parser.add_argument('--lang', type=str, nargs='+', default=['en'],
                    help='language filters')
args = parser.parse_args()

aws_credentials = dict(
    AWS_ACCESS_KEY_ID=os.environ.get("AWS_ACCESS_KEY_ID"),
    AWS_SECRET_ACCESS_KEY=os.environ.get("AWS_SECRET_ACCESS_KEY")
)

#client_params = dict(wait_on_rate_limit=True)
twitter_credentials = auth.get_twitter_credentials(aws_credentials)
stream = hourlyStream(twitter_credentials, args.rootdir)
stream.filter(languages=args.lang, track=args.track)