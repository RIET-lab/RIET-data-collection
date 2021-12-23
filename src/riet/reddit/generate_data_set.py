from praw import Reddit
from submission_encoder import SubmissionEncoder
from helpers import get_latest_posts, get_comments_from_url
import json


NUM_POSTS_TO_QUERY = 100
FILE_NAME = "data_set.json"
HESSEL_AND_LEE_SUBREDDITS = "AskMen+AskWomen+Fitness+LifeProTips+personalfinance+relationships"


def main():
    # Credentials for reddit stored in praw.ini, under the Test Script section
    reddit = Reddit("Test Script", user_agent="Data Collector by u/Arvonit")

    # # From the 500 latest posts from the Hessel and Lee subreddits, fetch the posts that are not
    # # stickied and have at least 30+ comments
    # subreddits = reddit.subreddit(HESSEL_AND_LEE_SUBREDDITS)
    # posts = get_latest_posts(reddit, subreddits, NUM_POSTS_TO_QUERY)

    # # Save the posts to a file
    # with open(FILE_NAME, "w") as file:
    #     json.dump(posts, file, indent=4, cls=SubmissionEncoder)
    # print(f"Saved {len(posts)} posts to {FILE_NAME}")

    # # Or print posts as JSON
    # print(json.dumps(posts, indent=4, cls=SubmissionEncoder))
    # print(len(posts))

    # Print out a random post's comments
    print(get_comments_from_url(
        reddit,
        "https://www.reddit.com/r/programming/comments/r0ifpa/microsoft_unveils_super_duper_secure_mode_in/"
    ))


if __name__ == "__main__":
    main()
