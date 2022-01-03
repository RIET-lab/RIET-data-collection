import pandas as pd
from pyarrow import parquet as pq
import os

def is_parquet(path):
    return path.split(".")[-1] == "parquet"

def count_tweets(root): 
    to_traverse = [root]
    N = 0
    while len(to_traverse) > 0:
        basepath = to_traverse.pop()
        for filename in os.listdir(basepath):
            path = os.path.join(basepath, filename)
            if is_parquet(path):
                table = pq.read_table(path)
                df = table.to_pandas()
                N += len(df)
            else:
                to_traverse.append(path)
    return N


root = "/home/mes21010/twitter_data"
N = count_tweets(root)
print(f"There have been {N} tweets collected in root dir {root}")
