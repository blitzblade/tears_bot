import tweepy
from time import sleep
from random import randint
import json, os, sys
from mongo_client import find_status, insert_status

def print_err(err):
    print(str(err) + " on line " + str(sys.exc_info()[2].tb_lineno))

def load_config():
    return json.load(open(os.path.join(sys.path[0],"config.json")))

config = load_config()



auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])

api = tweepy.API(auth)
KEY_WORD = "tears"
SCREEN_NAME = api.me()._json["screen_name"]

def follow_user(username):
    api.create_friendship(username)

def get_followers():
    screen_names = []
    for page in tweepy.Cursor(api.followers, screen_name=api.me()._json["screen_name"], count=200).pages():
        screen_names.extend([i._json["screen_name"] for i in page])
        print("LENGTH OF IDS ARRAY: ", len(screen_names))
        sleep(10)
    return screen_names 

def get_followers_and_tweet_tears():
    try:
        print(api.followers())
        for page in tweepy.Cursor(api.followers, screen_name=SCREEN_NAME, count=200).pages():
            screen_names = [i._json["screen_name"] for i in page]

            size = 20
            for i in range(0, len(screen_names), size):
                try:
                    sliced_screen_names = screen_names[i: i+size] #index will go out of range for last lap
                except IndexError:
                    sliced_screen_names = screen_names[i:]
                reply_to_tears_search(sliced_screen_names)

            print("LENGTH OF IDS ARRAY: ", len(screen_names))
            sleep(10)
    except Exception as e:
        print_err(e)

def get_text():
    with open('reply_text.txt') as f:
        return f.readlines()

def gen_text(text_list):
    i = randint(0, len(text_list)-1)
    return text_list[i]

def reply_to_tears_search(usernames,text=None):
    usernames = [f"from:{u}" for u in usernames]
    usernames = ", OR ".join(usernames)

    for tweet in tweepy.Cursor(api.search,q="tears ({})".format(usernames),rpp=100,result_type="recent", include_entities=True).items(100):
        print(tweet)
        print("=========================================================================")
        id = tweet._json["id"]
        if not text:
            text = gen_text(get_text())
        status = find_status(id)
        
        if f"@{SCREEN_NAME}" in tweet._json["text"]:
            print("Ignore this tweet. It's a reply to your tweet")
            continue

        if not status:
            if tweet.user._json["screen_name"] == SCREEN_NAME:
                print("Tweet belongs to bot...")
                continue

            print("status hasn't been updated...", status)
            api.update_status(text,in_reply_to_status_id=id, auto_populate_reply_metadata=True)
            status_obj = {
                "status_id": id,
                "text": text
            }
            insert_status(status_obj)
            print(tweet._json["text"])
            sleep(10)
        else:
            print("status has already been updated: ", status)

        print("=========================================================================")
                        

def reply_to_tears(username, text=None):
    for t in tweepy.Cursor(api.user_timeline, id=username, tweet_mode="extended").items(100):
        if "tears" in t._json["text"]:
            id = t._json["id"]
            if not text:
                text = gen_text(get_text())

            status = find_status(id)
            if not status:
                api.update_status(text,in_reply_to_status_id=id, auto_populate_reply_metadata=True)
                status_obj = {
                    "status_id": id,
                    "text": text
                }
                insert_status(status_obj)

            print("=========== TEARS ============")
            print(t._json["text"])
            print("=================== ==========")
        else:
            print("===========NO TEARS===========")
            print(t._json["text"])
            print("==============================")
    sleep(10)

if __name__=="__main__":
    get_followers_and_tweet_tears()
