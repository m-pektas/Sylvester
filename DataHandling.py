# -*- coding: utf-8 -*-


import re
import nltk as nlp
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd
from wordcloud import WordCloud,STOPWORDS
import matplotlib.pyplot as plt
import seaborn as sns
import tweepy


# nlp.data.path.append("./venv/nltk_data")
# nlp.download('punkt')
# nlp.download('stopwords')
# nlp.download('wordnet')
# nlp.download('vader_lexicon')

# HATA KODLARI
hatalar = { "Kişi bulunamadı." : 1} 


# TOKENS
consumer_key = "xxxxxxx"
consumer_secret = "xxxxxxx"
access_token = "xxxxxxx"
access_token_secret = "xxxxxxx"



#FUNCTIONS

# Get and Save User Tweets
def GetAndSaveUserTweets(username,tweetCount=500,database="./test.csv"):
    user_info = {}
    try:
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        auth.get_authorization_url()
        api = tweepy.API(auth)
    
        user = api.get_user(username)
    except tweepy.TweepError:
        print('Twitterdan data transferi gerçekleşmedi.')
        return hatalar["Kişi bulunamadı."]

    user_info["username"]=user.screen_name
    user_info["name"]=user.name
    user_info["description"]=user.description
    user_info["follower_count"]=user.followers_count
    user_info["followed_count"]=user.friends_count
    user_info["tweet_count"]=user.statuses_count
    user_info["web_url"]=user.url
    user_info["location"]=user.location
    user_info["lang"]=user.lang
    user_info["like_count"]=user.favourites_count
    user_info["profile_photo"]=user.profile_image_url
    
    print("Kullanıcı adı: " + user.screen_name)
    print("İsim: " + user.name)
    print("Açıklama: " + str(user.description))
    print("Takipçi: " + str(user.followers_count))
    print("Takip edilen: " + str(user.friends_count))
    print("Tweet sayısı: " + str(user.statuses_count))
    print("Web site: " + str(user.url))
    print("Kayıt tarihi: " + str(user.created_at))
    print("Lokasyon: " + str(user.location))
    print("Dil: " + str(user.lang))
    print("Favoriler: " + str(user.favourites_count))
    
    public_tweets = api.user_timeline(screen_name = username,count = tweetCount)
    #write_data(public_tweets,database)
    return user_info, public_tweets

"""
def write_data(public_tweets,fpath):
    print("Tweets loading..")
    f_data = open(fpath, "w")
    sayac = 1
    for tweet in public_tweets:
        f_data.write("Text:" + str(tweet.text.encode("utf-8"))+"\n")
        #f_data.write("\nTime:" + str(tweet.created_at))
        f_data.write("\n")
        sayac = sayac + 1
    print("Done.")    
"""

def checkAccount(username):
    
    result = GetAndSaveUserTweets(username=username) 
    if result == 1:
        return False,"-"
        
    global information
    global tweets
    information, tweets = result[0], result[1]
    
    AI()
    
    return True, information



def AI():
    
    dataset, all_tweets = dataCleaning()
    createWordcount(all_tweets=all_tweets)
    createPosAndNegWordcount(dataset)
    createEmotion(dataset)
    
    return True
    
    
    
    
def dataCleaning():
    data = {"Text":[]}
    #stops = ["text:b'","\\","rt","\n","http","co","xa","xe","ha"]
    for t in tweets:
        x = t.text.encode("utf-8")
        x = str(x)
        x = str.lower(x)
        x = x.replace("text:b'","").replace("\\"," ").replace("rt","").replace("\n","")
        x = re.sub("[^a-zA-z]", " ",x) 
        x =  nlp.word_tokenize(x)
        lemma = nlp.WordNetLemmatizer()
        x = [lemma.lemmatize(i) for  i in x]
        x = [i for i in x if len(i)>2]
        x = " ".join(x)
        data["Text"].append(x)
    
    dataset = pd.DataFrame().from_dict(data)
    dataset = dataset[ dataset["Text"] != ""]
    all_tweets = " ".join(dataset["Text"])
    
    return dataset, all_tweets

    
    
def createWordcount(all_tweets,filename="_wordcount.png",tag = "wordcount"):
    stopwords = ["x","s","xa","t","co","wa","rt","xe"]
    stopwords = stopwords + list(STOPWORDS)
 
    wordcloud = WordCloud(width = 800, height = 800, 
                    background_color ='white', 
                    stopwords = stopwords, 
                    min_font_size = 12).generate(all_tweets) 
      
    # plot the WordCloud image                        
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0)
    information[tag] = "../static/db/"+str(information["username"])+filename
    plt.savefig("./static/db/"+str(information["username"])+filename)

def createPosAndNegWordcount(dataset):
    sid = SentimentIntensityAnalyzer()
    pos_list = []
    neg_list = []
    for i in dataset["Text"]:
        pos, neg = sid.polarity_scores(i)["pos"], sid.polarity_scores(i)["neg"]
        if pos > neg:
            pos_list.append(i)
        elif neg > pos:
            neg_list.append(i)
    
    pos_tweets = " ".join(pos_list)
    neg_tweets = " ".join(neg_list)
     
    createWordcount(pos_tweets,filename="_pos_wordcount.png", tag = "pos_wordcount")
    createWordcount(neg_tweets,filename="_neg_wordcount.png", tag = "neg_wordcount")   
    

def createEmotion(dataset):
    sid = SentimentIntensityAnalyzer()
    dicts = {"neg":0,"neu":0,"pos":0}
    for i in dataset["Text"]:
        dicts["neg"] =  dicts["neg"] + sid.polarity_scores(i)["neg"]
        dicts["neu"] =  dicts["neu"] + sid.polarity_scores(i)["neu"]
        dicts["pos"] =  dicts["pos"] + sid.polarity_scores(i)["pos"]
        
    total = sum(dicts.values())
    dicts["neg"] = dicts["neg"] / total
    dicts["neu"] = dicts["neu"] / total
    dicts["pos"] = dicts["pos"] / total
    
    emotion = list(dicts.keys())
    values = list(dicts.values())
        
    
    plt.subplots(figsize=(8,6))
    ax = sns.barplot(x=emotion, y=values)
    plt.title("Sentiments")
    plt.xlabel("Emotions")
    plt.ylabel("Percent")
    information["emotions"] = "../static/db/"+str(information["username"])+"_emotions.png"
    plt.savefig("./static/db/"+str(information["username"])+"_emotions.png")
    
    
    
