from pymongo import MongoClient

client = MongoClient()
db = client.tweets_db

statuses = db.statuses

def insert_status(status):
    return statuses.insert_one(status)

def find_status(status_id):
    return statuses.find_one({"status_id": status_id})
