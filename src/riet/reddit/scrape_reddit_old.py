from typing import Optional
from praw import Reddit
from praw.models import Submission
from datetime import datetime
from praw.models.helpers import SubredditHelper
import json


NUM_POSTS_TO_FETCH = 100
CLIENT_ID = "QEEh-LDPV1Tb_E6i2DBvkg"
CLIENT_SECRET = "IWreFD1UvVq7f9pKNYsQoQoMujlCBQ"
USERNAME = ""
PASSWORD = ""


def main() -> None:
    reddit = Reddit(client_id=CLIENT_ID,
                    client_secret=CLIENT_SECRET,
                    username=USERNAME,
                    password=PASSWORD,
                    user_agent="Data Collector by u/Arvonit")
    posts = []
    subreddits = reddit.subreddit(
        "AskMen+AskWomen+Fitness+LifeProTips+personalfinance+relationships"
    )

    # Scrape the newest 100 posts from the subreddits
    for post in subreddits.new(limit=NUM_POSTS_TO_FETCH):
        # Only get non-stickied submissions with at least 30 comments
        if not post.stickied and post.num_comments >= 30:
            title = post.title
            upvote_percentage = round(post.upvote_ratio * 100, 2)
            # Convert date from unix time to local time zone
            date = datetime.fromtimestamp(post.created_utc).strftime("%Y-%m-%d %H:%M")
            body = post.selftext
            author = post.author.name if post.author is not None else "No author"
            num_comments = post.num_comments
            comments = get_comments(post)
            id = post.id
            posts.append(Post(title, body, date, author,
                              upvote_percentage, num_comments, comments, id))
            # posts.append(post)

            # post.comments.replace_more(limit=None)  # Now let's recreate the comment tree
            # comments = post.comments[:]  # Make a copy of the comments

    # Convert posts to JSON and save it to a file
    # with open("data.json", "w") as file:
    #     json.dump([get_json(post) for post in posts], file, indent=4)
    # print(len(posts))

    # Print posts in JSON format
    print(json.dumps([get_json(post) for post in posts], indent=4))
    print(len(posts))

    # Print out all the data
    # for i in range(len(posts)):
    #     title, upvote_percentage, date, comments_num, comments = posts[i]
    #     print("-" * 100)
    #     print(f"{i + 1}. | Title: '{title}' | Upvote %: {upvote_percentage} | Date: {date} | Comments: {comments_num}")

    #     # while comments:
    #     #     comment = comments.pop(0)
    #     #     print("-" * 20)
    #     #     print(comment.body)
    #     #     comments.extend(comment.replies)

    #     # Print out comments
    #     # for comment, depth in comments:
    #     #     print("-" * 20)
    #     #     print(f"{'    ' * depth}{comment}")

    #     print("-" * 100)


def process_comment(comment, depth=0):
    # Generator that will generate all comments aligning with the depth
    # yield comment.body, depth
    # for reply in comment.replies:
    #     yield from process_comment(reply, depth + 1)
    yield Comment(comment.body, depth, comment.author.name if comment.author is not None else "No author", comment.id)
    for reply in comment.replies:
        yield from process_comment(reply, depth + 1)


def get_comments(post, more_limit=32):
    # Create a list of comments + depth using the generator above
    # comments = []
    # post.comments.replace_more(limit=more_limit)
    # for top_level in post.comments:
    #     comments.extend(process_comment(top_level))
    # return comments
    comments = []
    post.comments.replace_more(more_limit)
    for comment in post.comments:
        comments.extend(process_comment(comment))
    return comments


def get_json(obj):
    return json.loads(json.dumps(obj, default=lambda o: getattr(o, '__dict__', str(o))))


class Comment:
    def __init__(self, body: str, depth: int, author: str, id: Optional[int] = None):
        self.body = body
        self.depth = depth
        self.author = author
        self.id = id


class Post:
    def __init__(self,
                 title: str,
                 body: str,
                 date: datetime,
                 author: str,
                 upvote_percentage: float,
                 num_comments: int,
                 comments: list[Comment],
                 id: Optional[int] = None):
        self.title = title
        self.body = body
        self.date = date
        self.author = author
        self.upvote_percentage = upvote_percentage
        self.num_comments = num_comments
        self.comments = comments
        self.id = id


if __name__ == "__main__":
    main()
