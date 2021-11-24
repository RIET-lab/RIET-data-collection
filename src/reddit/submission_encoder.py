from json import JSONEncoder
from praw.models.comment_forest import CommentForest
from praw.reddit import Comment, Submission
from datetime import datetime


class SubmissionEncoder(JSONEncoder):
    """
    An encoder used to serialize a Reddit post (`Submission` in PRAW) to JSON.
    """

    def default(self, obj: Submission):
        if isinstance(obj, Submission):
            id = obj.id
            title = obj.title
            upvote_percentage = round(obj.upvote_ratio * 100, 2)
            # Convert date from unix time to UTC
            date = datetime.utcfromtimestamp(obj.created_utc).strftime("%Y-%m-%d %H:%M")
            body = obj.selftext
            author = obj.author.name
            num_comments = obj.num_comments
            comments = self._serialize_comments(obj.comments)
            return {
                "post_id": id,
                "title": title,
                "body": body,
                "date": date,
                "author": author,
                "upvote_percentage": upvote_percentage,
                "num_comments": num_comments,
                "comments": comments
            }

        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)

    def _serialize_comments(self, comments: CommentForest, more_limit=32) -> list:
        """
        Serializes the comment tree of a reddit post into a JSON tree.
        """
        def helper(comment: Comment, depth=0):
            out = {
                "comment_id": comment.id,
                "body": comment.body,
                "author": comment.author.name if comment.author is not None else "",
                "depth": depth,
                "replies": [helper(reply, depth + 1) for reply in comment.replies]
            }
            return out

        out = []
        comments.replace_more(more_limit)
        for comment in comments:
            out.append(helper(comment))
        return out
