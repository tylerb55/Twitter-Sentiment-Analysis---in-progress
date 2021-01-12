# -*- coding: utf-8 -*-

import tweepy
import json
import re
import nltk
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords, wordnet
from PreProcessor import RepeatReplacer
import csv
import time 
import datetime


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

import sqlite3
import datetime

from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database 
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return conn
            

def create_table(conn, create_table_sql):
    """ create a table from the creat_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)
        
        
def insert_tweet(conn, tweet):
    """" insert data into the table at the specified column
    :param : 
    :return:
    """
    date = datetime.date.today()
    sql = ''' INSERT INTO tweets(id,trend,collected_on,sentiment)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, tweet)
    conn.commit()
    return cur.lastrowid
    
def insert_trend(conn, trend):
    """" insert data into the table at the specified column
    :param : 
    :return:
    """
    date = datetime.date.today()
    sql = ''' INSERT INTO trends(trend, collected_on, positive_tweets, negative_tweets, neutral_tweets, mode_sentiment)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, trend)
    conn.commit()
    return cur.lastrowid


def close_connection(conn):
    if conn:
        conn.close() 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -  


auth = tweepy.OAuthHandler('4rgroM1SkDgWk3AEEMmXjATOO', 'rRbKxGCdBx9PTrKa0LHO7LZkjeZm2ngojSS0EtQxhvS34u2jKX')
auth.set_access_token('1319341988995649538-uqHxfZI6estF2f8Yc0U28gqBY3MmY4', 'bkj2lvX0yCbnhKEFn0EhlSxR4gPxRWgsq46R2CA8eMUi2')
stop_words = set(stopwords.words('english') + list(punctuation) + ['USER','URL'])

api = tweepy.API(auth)
replacer = RepeatReplacer()
#print(api.verify_credentials())

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def preproccess_tweet(tweet):
    tweet = tweet.lower()
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', tweet)#replace www. and https// with the token URL
    tweet = re.sub('@[^\s]+', 'USER', tweet)#replace usernames with the tag USER
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet) # remove the # from hastags
    tweet = word_tokenize(tweet)#remove repeated characters in words        
    return [replacer.replace(word) for word in tweet if word not in stop_words and '.' not in word]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def processTweets(list_of_tweets):
        processedTweets=[]
        for tweet in list_of_tweets:
            processedTweets.append((preproccess_tweet(tweet["tweet_text"]),tweet["sentiment"]))
        return processedTweets

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def save_to_csv(tweets):
    
    with open('training_set.csv', mode='a', encoding="utf-8", newline='') as csv_file:
        fieldnames = ['text', 'trend', 'sentiment','id']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        for row in tweets:
            writer.writerow(row)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -    
    
def buildTrainingSet(corpusFile):    
    #rate_limit=180
    #sleep_time=900/rate_limit
    trainingDataSet = []
    
    # read the data from the hand classified csv file
    with open(corpusFile,'rt') as csvfile:
        lineReader=csv.reader(csvfile, delimiter=',',quotechar="\"")
        for row in lineReader:
            trainingDataSet.append({"tweet_text":row[0],"trend":row[1], "sentiment":row[2], "tweet_id":row[3]})
    return trainingDataSet
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    
corpusFile = "C:/Users/Tyler/Desktop/Work/390/project/training_set.csv"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def buildDictionary(PreProcessedtrainingData):
    dictionary = []
    
    for (words, sentiment) in PreProcessedtrainingData:
        dictionary.extend(words)
        
    wordlist = nltk.FreqDist(dictionary)
    wordfeatures = wordlist.keys()
    
    return wordfeatures

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def extract_features(tweet):
    tweet_words=set(tweet)
    features={}
    for word in word_features:
        features['contains(%s)' % word]=(word in tweet_words)
    return features 
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def train_classifier():
    print('train the classifier. give accuracy of classifier')

def get_sentiment():
    print('an overall score for the sentiment of the tweet using dictionary and classifier')
    
def store_results(tweets, sentiment_analysis):
    print('put me in a database')

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def get_UKtrends():
    #sets the WOEID location to the United Kingdom to collect United Kingdom trends
    trends = api.trends_place(23424975)

    data = trends[0] 
    # grab the trends
    trends = data['trends']
    # grab the names from the current top 5 trends
    names = [trend['name'] for trend in trends[:5]]
    return names
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def add_to_trainingSet(trend, NO_tweets):
    tweets = []
    fetched_tweets = api.search(q=trend, count=NO_tweets, lang='en')
    for tweet in fetched_tweets:
        parsed_tweet = {}
        parsed_tweet['text']='"'+tweet.text+'"'
        parsed_tweet['trend']='"'+trend+'"'
        parsed_tweet['sentiment']='""'
        parsed_tweet['id']='"'+tweet.id+'"'
        if tweet.retweet_count > 0: 
            # if tweet has retweets, ensure that it is appended only once 
            if parsed_tweet not in tweets: 
                tweets.append(parsed_tweet)
        else:
            tweets.append(parsed_tweet)
    save_to_csv(tweets)
    return tweets
  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def get_tweets(trend, NO_tweets):
    """ returns test set
    param trend: the trend term the tweets are going to be searched on
    param NO_tweets: the number of tweets to collect
    return: array object containing the relevant information for each tweet"""
    testSet = []
    fetched_tweets = api.search(q=trend, count=NO_tweets, lang='en')
    for tweet in fetched_tweets:
        parsed_tweet = {}
        parsed_tweet['tweet_text']=tweet.text
        parsed_tweet['trend']=trend
        parsed_tweet['sentiment']=''
        parsed_tweet['id']=tweet.id_str
        if tweet.retweet_count > 0: 
            # if tweet has retweets, ensure that it is appended only once 
            if parsed_tweet not in testSet: 
                testSet.append(parsed_tweet)
        else:
            testSet.append(parsed_tweet)
    return testSet
  
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def main():
    """main function"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
db=r"C:\sqlite\db\tweetSentiments.db"
conn = create_connection(db)

testSet = []
trainingData = buildTrainingSet(corpusFile)
trends=get_UKtrends()
for i in range(5):
    testSet.append(get_tweets(trends[i], 3)[0])
        
preprocessedTrainingSet = processTweets(trainingData)
preprocessedTestSet = processTweets(testSet)

word_features = buildDictionary(preprocessedTrainingSet)
trainingFeatures = nltk.classify.apply_features(extract_features, preprocessedTrainingSet)
    
NBayesClassifier = nltk.NaiveBayesClassifier.train(trainingFeatures)

NBResultLabels = []

tweets_parsed=0
for tweet in preprocessedTestSet:
    NBResultLabels.append([testSet[tweets_parsed]['trend'],NBayesClassifier.classify(extract_features(tweet[0]))]) 
    testSet[tweets_parsed]['sentiment']= NBayesClassifier.classify(extract_features(tweet[0]))
    data=(testSet[tweets_parsed]['id'],testSet[tweets_parsed]['trend'],datetime.date.today(),testSet[tweets_parsed]['sentiment'])
    insert_tweet(conn,data)
    tweets_parsed+=1
    #insert testSet[tweets_parsed] into database

print(testSet)    
print(preprocessedTestSet)
print(NBResultLabels)

# ------------------------------------------------------------------------

# get the majority vote
if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
    #update database with count
    print("Overall Positive Sentiment")
    print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
else: 
    print("Overall Negative Sentiment")
    print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")



    
