# RIET-data-collection
data collection repo for RIET lab

### Install and Requirements
#### Prerequisites 
Install via this command for twitter related usage:
```
conda install --file requirements.txt
```

#### Install
If prereqs are installed then simply run
```
pip install .
```

### Run Stream
This will continously collect tweets from a tweepy stream with words to track and languages to filter by. Stores in parquet files for efficient reading in a temporal structure in given root directory.

Uses AWS credentials to access secrets manager to get twitter credentials via env variables `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
```
python run.py --rotdir <> --track <> ... <> --lang <> ... <>
```

### Run Stream Alerts
Running this script will check every hour is new tweets were added, otherwise it will send failure emails to RIET members to create a fix
```
python alert.py --rootdir <> --from_who <> --password <> --to <> ... <> 
```
