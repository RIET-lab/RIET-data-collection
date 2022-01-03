import smtplib
import pandas as pd
from pyarrow import parquet as pq
import os
import datetime
import time
import argparse

parser = argparse.ArgumentParser(description='run a twitter stream')
parser.add_argument('--rootdir', type=str, default=".",
                    help='root directory of stream collection')
parser.add_argument('--from_who', type=str, default="",
                    help='email from')
parser.add_argument('--password', type=str, default="",
                    help='email password')
parser.add_argument('--to', type=str, nargs='+', default=[],
                    help='emails to alert')
args = parser.parse_args()

def sendmail(from_who, password, to, subject, msg):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(from_who, password)
    msg = 'Subject: {}\n\n{}'.format(subject, msg)
    s.sendmail(from_who, to, msg)
    s.quit()

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

class StreamChecker:
    def __init__(self, root):
        self.root = root
        t = datetime.datetime.now()
        self.year = t.year
        self.month = t.month
        self.day = t.day
        self.hour = t.hour
        self.tweet_count = count_tweets(self.root)
        self.template = """Dear lovely RIET members,
You are getting this email because no new tweets came for the time {}... Immediately fix this
        
Sincerely,
your friendly neigborhood stream checker"""

    def timeshift(self):
        t = datetime.datetime.now()
        year = t.year
        month = t.month
        day = t.day
        hour = t.hour
        if t.year != self.year or \
            t.month != self.month or \
            t.day != self.day or \
            t.hour != self.hour:
            
            self.year = year
            self.month = month
            self.day = day
            self.hour = hour
            return True

        return False       

    def send_email(self):
        message = self.template.format(f"{self.month}/{self.day}/{self.year} {self.hour}:00")
        from_who = args.from_who
        from_who_password = args.password
        to = args.to
        subject = "RIET Twitter Streams Issue"
        sendmail(
            from_who, 
            from_who_password, 
            to, 
            subject, 
            message)

    def run(self):
        while True:
            if self.timeshift():
                n_tweets = count_tweets(self.root)
                if n_tweets == self.tweet_count:
                    self.send_email()
                else:
                    self.tweet_count = n_tweets
            time.sleep(300)


checker = StreamChecker(args.rootdir)
checker.run()
