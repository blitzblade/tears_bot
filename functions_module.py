import tweepy
from time import sleep
from random import randint
import json, os, sys
from mongo_client import find_status, insert_status
from nltk.corpus import stopwords 
from nltk.tokenize import RegexpTokenizer
import nltk
# nltk.download('stopwords')

# stop_words = stopwords.words('english')

def print_err(err):
    print(str(err) + " on line " + str(sys.exc_info()[2].tb_lineno))

def load_config():
    return json.load(open(os.path.join(sys.path[0],"config.json")))

config = load_config()
auth = tweepy.OAuthHandler(config["consumer_key"], config["consumer_secret"])
auth.set_access_token(config["access_token"], config["access_token_secret"])

api = tweepy.API(auth)#, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
KEY_WORD = "tears"
SCREEN_NAME = api.me()._json["screen_name"]

def follow_user(username):
    try:
        api.create_friendship(username)
    except Exception as ex:
        print_err(ex)

def like(id):
    try:
        api.create_favorite(id)
    except Exception as ex:
        print_err(ex)

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
                        

def blow_up():
    tweets = tweepy.Cursor(api.search,q="blow ({})".format(SCREEN_NAME),rpp=100,result_type="recent", include_entities=True).items(100)
    

    for t in tweets:
        print(f"====================>>>>>>>>>>>>>> >>>>>>>>>>>>>>>>>>>=======================")
        # print(t)
        t_id = t._json["id"]
        t_status = find_status(t_id)

        if t_status:
            print("status handled already")
            continue
        like(t_id)
        api.update_status("Wait while I do my thing. Thank me later... :D",in_reply_to_status_id=t_id, auto_populate_reply_metadata=True)
        screen_name, status_id = t._json["in_reply_to_screen_name"], t._json["in_reply_to_status_id"]

        if screen_name and status_id:
            parent_status = api.get_status(t._json['in_reply_to_status_id'], tweet_mode="extended")
            
            text = parent_status._json["full_text"]
            print(text)
            tokenizer = RegexpTokenizer(r'\w+')
            words = sorted(tokenizer.tokenize(text),key=len)[-4:]
            search_term = "({})".format(", OR ".join(words)) 
            print(search_term)
            parent_status_link = "https://twitter.com/{}/status/{}".format(screen_name, status_id)

            results = tweepy.Cursor(api.search,q=search_term,result_type="popular", include_entities=True).items(50)
            if not results:
                api.update_status("No related top tweets to tag along :(",in_reply_to_status_id=t._json["id"], auto_populate_reply_metadata=True)
            for r in results:
                id = r._json["id"]
                
                stored_tweet = find_status(id)
                if not stored_tweet:
                    like(id)
                    print("About to update status search result...")
                    api.update_status("Kindly like this tweet or retweet. You are the best! \n{}".format(parent_status_link),in_reply_to_status_id=r._json["id"], auto_populate_reply_metadata=True)
                    print(r._json["text"])
                    sleep(5)
                    status_obj = {
                        "status_id": id,
                        "text": r._json["text"]
                    }
                    insert_status(status_obj)
        else:
            print("NO STATUS TO BLOW UP")
            api.update_status("No tweet to blow up... :(",in_reply_to_status_id=t._json["id"], auto_populate_reply_metadata=True)
            sleep(30)

        t_status_object = {
                        "status_id": t_id,
                        "text": t._json["text"]
                        }
        insert_status(t_status_object)
        print("====================>>> END <<<==============================================")



#getting stalkers
def reply_to_tcreate_favoriteears(username, text=None):
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