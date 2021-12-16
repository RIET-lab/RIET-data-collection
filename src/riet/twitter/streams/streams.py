import tweepy
from collections import defaultdict
import pyarrow as pa
from pyarrow import parquet as pq
import json
import datetime
import time
import os

# twitter stream
class hourlyStream(tweepy.Stream):
    def __init__(self, credentials, root_path):
        # stores data
        super().__init__(credentials.get("consumer_key"),
            credentials.get("consumer_secret"),
            credentials.get("access_token"),
            credentials.get("access_token_secret"))
        self.data = defaultdict(list)
        self.colmap = dict(
            created_at="created_at",
            id="id",
            text="text",
            #conversation_id="conversation_id",
            #author_id="author_id"
        )
        self.root_path = root_path
        self.dir = None

        # starting time
        t = datetime.datetime.now()
        self.year = t.year
        self.month = t.month
        self.day = t.day
        self.hour = t.hour
    
    def _get_file_dir(self):
        path =  os.path.join(self.root_path, 
            str(self.year),
            str(self.month),
            str(self.day))
        if not os.path.exists(path):
            os.makedirs(path)
            print("CREATED DIRECTORY {}".format(path))
        return path

    def _get_file_path(self):
        path_dir = self._get_file_dir()
        filename = f"{self.hour}.parquet"
        return os.path.join(path_dir, filename)
    
    def _write_data(self):
        path = self._get_file_path()
        try:
            table = {k: pa.array(v) for k,v in self.data.items()}
            table = pa.Table.from_pydict(table)
            pq.write_table(table, path)
            print("WROTE TO PATH <{}> with <{}> items".format(path, len(list(self.data.values())[0])))

        except Exception as e:
            print('Failed with error _write_data:', str(e))
            time.sleep(1)

        self.data = defaultdict(list)

    def _add_data(self, data):
        if "limit" in data.keys(): return
        for k1, k2 in self.colmap.items():
            self.data[k1].append(data[k2])

    def _update(self):
        """Updates date and writes if needed
        """
        t = datetime.datetime.now()
        year, month, day, hour = t.year, t.month, t.day, t.hour
        if year != self.year or \
                month != self.month or \
                day != self.day or \
                hour != self.hour:
            self._write_data()
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour

    def on_data(self, data):
            try:
                self._update()
                self._add_data(json.loads(data))

            except Exception as e:
                print('Failed with error on_data:', str(e))
                if not data is None:
                    print(json.loads(data))
                time.sleep(1)

    def on_error(self, status):
        print(status)