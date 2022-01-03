import json
from . import get_conversation

class placeholder_tweet:
    text = ""
    author_id = ""
    created_at = None
    is_placeholder = True

    def __init__(self, node_id):
        self.id = node_id

class TweetNode:
    """
    Class to handle tweets
    """
    def __init__(self, tweet):
        self.tweet = tweet
        self.parents = set()
        self.children = set()
        
    def add_parent(self, parent):
        self.parents.add(parent)
        
    def add_child(self, child):
        self.children.add(child)
        
    def is_placeholder(self):
        return hasattr(self.tweet, "is_placeholder")
    
    def __getitem__(self, item):
        """
        Interfacing tweet properties
        """
        return self.tweet.get(item)
        
    def __hash__(self):
        return self.tweet.id
    
    def __str__(self):
        return self.convert_tweet_to_string(self.tweet)
        
    @classmethod
    def placeholder(cls, node_id):
        return cls(placeholder_tweet(node_id))
    
    @staticmethod
    def convert_tweet_to_string(tweet):
        tweet_dic = dict(
            author = tweet.author_id,
            text = tweet.text,
            created_at = tweet.created_at
        )
        return json.dumps(tweet_dic)
    
class TweetTree:
    """
    Class to handle tweet tree
    """
    nodes = {}
    
    def __init__(self, root):
        self.root = root
        
    def __getitem__(self, node_id):
        return self.nodes.get(node_id)
    
    def __len__(self):
        return len(self.nodes)
    
    @property
    def size(self):
        return len(self)
    
    @property
    def depth(self):
        cur_nodes = [self.root]
        depth = 1
        while True:
            next_level = []
            for node in cur_nodes:
                next_level.extend(node.children)
            if len(next_level): 
                depth += 1
                cur_nodes = next_level
            else: break
        return depth
    
    @classmethod
    def from_node(cls, client, node, is_root=False):
        """
        Will make API calls to generate tree from single node
        """
        cls.from_conversation_id(client, 
                                  node.tweet.conversation_id, 
                                  node if is_root else None)
    
    @classmethod
    def from_conversation_id(cls, client, conversation_id, root=None, verbose=False):
        """
        Will make API calls to generate tree from conversation id
        """
        tweets = get_conversation(client, conversation_id, get_root=root is None, verbose=verbose)
        tweets = [TweetNode(tweet) for tweet in tweets]
        tree = cls(tweets[0])
        tree.nodes = cls.fill_in_nodes(tweets)
        return tree
        
    @staticmethod
    def fill_in_nodes(nodes):
        node_dict = {}
        for node in nodes: node_dict[hash(node)] = node
        
        for node in nodes:
            parents = node.tweet.referenced_tweets or []
            for parent in parents:
                parent_node = node_dict.get(parent.id, TweetNode.placeholder(parent.id))
                parent_node.add_child(node)
                node.add_parent(parent_node)
                
        return node_dict