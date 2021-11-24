from praw.models.helpers import SubredditHelper
from praw.reddit import Reddit
import json
from submission_encoder import SubmissionEncoder


def get_latest_posts(reddit: Reddit, subreddits: SubredditHelper, num_to_fetch: int = 100):
    posts = []
    # Query the `num_to_fetch` latest posts from subreddits specified in `subreddits` and add
    # those with at least 30 comments
    for post in subreddits.new(limit=num_to_fetch):
        # Only add non-stickied posts with at least 30 comments
        if not post.stickied and post.num_comments >= 30:
            posts.append(post)
    return posts


def get_comments_from_url(reddit: Reddit, url: str) -> str:
    """
    Returns the post from the given Reddit post URL as a JSON string.
    """
    # Get a `Submission` by its url
    post = reddit.submission(url=url)
    # Serialize the post and return it
    return json.dumps(post, indent=4, cls=SubmissionEncoder)
