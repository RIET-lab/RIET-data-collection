from __future__ import annotations
from json.encoder import JSONEncoder
from datetime import datetime
import copy


class Tweet:
    def __init__(self, data: dict):
        self.data = data  # dict
        self.parent = None  # Optional[Tweet]
        self.replies = set()  # set[Tweet]

    def __getitem__(self, attribute: str):
        return self.data[attribute]


class TweetEncoder(JSONEncoder):
    def default(self, obj: Tweet):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Tweet):
            # for attribute in obj.data.__slots__:
            #     if attribute != "data" and obj.data[attribute] is not None:
            #         out[attribute] = obj.data[attribute]
            # out = copy.deepcopy(obj.data)

            # Add parent_id and replies to data
            out = copy.deepcopy(obj.data.data)
            if obj.parent is not None:
                out.update({"parent_id": obj.parent["id"]})
            if len(obj.replies) > 0:
                out.update({"replies": [self.default(reply) for reply in obj.replies]})

            return out

        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, obj)
