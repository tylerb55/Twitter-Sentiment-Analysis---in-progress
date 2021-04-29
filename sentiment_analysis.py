# -*- coding: utf-8 -*-

import tweepy
import re
import nltk
from nltk.tokenize import word_tokenize
from string import punctuation
from nltk.corpus import stopwords, wordnet
from PreProcessor import RepeatReplacer
import csv
import datetime
import pickle
import pandas as pd

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

import sqlite3
from sqlite3 import Error

db=r"C:\sqlite\db\tweetSentiments.db"

con = sqlite3.connect(db)
trends = pd.read_sql_query("SELECT * FROM trends", con)

con.close()

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
    sql = ''' INSERT INTO tweets(id,trend,collected_on,sentiment)
              VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET id=id'''
    cur = conn.cursor()
    cur.execute(sql, tweet)
    conn.commit()
    return cur.lastrowid
    
def insert_trend(conn, trend):
    """" insert data into the table at the specified column
    :param : 
    :return:
    """
    sql = ''' INSERT INTO trends(trend, collected_on, positive_tweets, negative_tweets, neutral_tweets)
              VALUES(?,?,?,?,?) ON CONFLICT(trend,collected_on) DO UPDATE SET trend=trend'''
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
    
    with open('training_set.csv', mode='a', encoding='utf-8', newline='') as csv_file:
        fieldnames = ['text', 'trend', 'sentiment','id']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        for row in tweets:
            writer.writerow(row)

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -    
    
def buildTrainingSet(corpusFile):    
    trainingDataSet = []
    
    # read the data from the hand classified csv file
    with open(corpusFile,'rt',encoding ="utf-8") as csvfile:
        lineReader=csv.reader(csvfile, delimiter=',',quotechar="\"")
        for row in lineReader:
            trainingDataSet.append({"tweet_text":row[0],"trend":row[1], "sentiment":row[2], "tweet_id":row[3]})
    return trainingDataSet
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 


def buildTestSet(File):    
    testDataSet = []
    
    # read the data from the hand classified csv file
    with open(corpusFile,'rt',encoding ="utf-8") as csvfile:
        lineReader=csv.reader(csvfile, delimiter=',',quotechar="\"")
        for row in lineReader:
            testDataSet.append({"tweet_text":row[0],"sentiment":row[2]})
    return testDataSet
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

    
corpusFile = "C:/Users/Tyler/Desktop/Work/390/project/training_test_set.csv"
testFile = "C:/Users/Tyler/Desktop/Work/390/project/test_set.csv"

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
    #pass word_features by parameter
    for word in word_features:
        features['contains(%s)' % word]=(word in tweet_words)
    return features 

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def get_UKtrends():
    #sets the WOEID location to the United Kingdom to collect United Kingdom trends
    trends = api.trends_place(23424975)

    data = trends[0] 
    # grab the trends
    trends = data['trends']
    # grab the names from the current top 5 trends
    names = [trend['name'] for trend in trends[:10]]
    return names
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def add_to_trainingSet(trend, NO_tweets):
    tweets = []
    fetched_tweets = api.search(q=trend, count=NO_tweets, lang='en')# NOT POPULAR, WE GET NO RESULTS
    for tweet in fetched_tweets:
        parsed_tweet = {}
        parsed_tweet['text']=tweet.text
        parsed_tweet['trend']=trend
        parsed_tweet['sentiment']=''
        parsed_tweet['id']=tweet.id_str
        if tweet.retweet_count > 0: 
            # if tweet has retweets, ensure that it is appended only once 
            if parsed_tweet not in tweets: #text isnt in tweets FIX IT 
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
    
def TestClassifier():
    date = datetime.date.today()
    
    testSet = buildTestSet(testFile)
    preprocessedTestSet = []
    
    trends=get_UKtrends()        
    preprocessedTestSet=processTweets(testSet)
        
    f = open('NB_Sentiment_Classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    NBayesClassifier = classifier
        
    NBResultLabels = []
    
    tweets_parsed=0
    positive=0
    negative=0
    neutral=0
    correct=0
    wrong=0
        
    for tweet in preprocessedTestSet:
        sentiment=NBayesClassifier.classify(extract_features(tweet[0]))
        NBResultLabels.append(sentiment) 
        if testSet[tweets_parsed]['sentiment']==sentiment:
            correct+=1
        else:
            wrong+=1
        tweets_parsed+=1
        if(sentiment=="positive"):
            positive+=1
        elif(sentiment=="neutral"):
            neutral+=1
        elif(sentiment=="negative"):
            negative+=1

    # ------------------------------------------------------------------------
    print("Precision = " + str(correct/len(NBResultLabels)*100) + "%")
    
    # get the majority vote
    if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
        #update database with count
        print("Overall Positive Sentiment")
        print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
    else: 
        print("Overall Negative Sentiment")
        print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

def one_term(search_term):
    conn = create_connection(db)
    date = datetime.date.today()
    
    testSet = []
    preprocessedTestSet = []
    
    testSet.append(get_tweets(search_term, 100 ))
    preprocessedTestSet.append(processTweets(testSet[0]))
        
    f = open('NB_Sentiment_Classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    NBayesClassifier = classifier
        
    NBResultLabels = []

    tweets_parsed=0
    positive=0
    negative=0
    neutral=0
    for tweet in preprocessedTestSet[0]:
        sentiment=NBayesClassifier.classify(extract_features(tweet[0]))
        NBResultLabels.append(sentiment) 
        testSet[0][tweets_parsed]['sentiment']= sentiment
        data=(testSet[0][tweets_parsed]['id'],testSet[0][tweets_parsed]['trend'],date,testSet[0][tweets_parsed]['sentiment'])
        insert_tweet(conn,data)
        tweets_parsed+=1
        if(sentiment=="positive"):
            positive+=1
        elif(sentiment=="neutral"):
            neutral+=1
        elif(sentiment=="negative"):
            negative+=1
    trend_data=[testSet[0][0]['trend'], date, positive, negative, neutral]
    df = pd.DataFrame(index=[0],columns=['trend','collected_on','positive_tweets','negative_tweest','neutral_tweets'] )
    df.loc[0] = trend_data#insert_trend(conn,trend_data)
        #insert testSet[tweets_parsed] into database
    df = df.append(trends, ignore_index=True)


    # ------------------------------------------------------------------------
    
    # get the majority vote
    if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
        #update database with count
        print("Overall Positive Sentiment")
        print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
    else: 
        print("Overall Negative Sentiment")
        print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")
    
    return df
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
def main():
    """main function"""
    conn = create_connection(db)
    date = datetime.date.today()
    
    testSet = []
    preprocessedTestSet = []
    
    trends=get_UKtrends()
    for i in range(5):
        testSet.append(get_tweets(trends[i], 100 ))
        preprocessedTestSet.append(processTweets(testSet[i]))
        
    f = open('NB_Sentiment_Classifier.pickle', 'rb')
    classifier = pickle.load(f)
    f.close()
    NBayesClassifier = classifier
        
    NBResultLabels = []

    for n in range(5):
        tweets_parsed=0
        positive=0
        negative=0
        neutral=0
        for tweet in preprocessedTestSet[n]:
            sentiment=NBayesClassifier.classify(extract_features(tweet[0]))
            NBResultLabels.append(sentiment) 
            testSet[n][tweets_parsed]['sentiment']= sentiment
            data=(testSet[n][tweets_parsed]['id'],testSet[n][tweets_parsed]['trend'],date,testSet[n][tweets_parsed]['sentiment'])
            insert_tweet(conn,data)
            tweets_parsed+=1
            if(sentiment=="positive"):
                positive+=1
            elif(sentiment=="neutral"):
                neutral+=1
            elif(sentiment=="negative"):
                negative+=1
        trend_data=(testSet[n][0]['trend'], date, positive, negative, neutral)
        insert_trend(conn,trend_data)


    # ------------------------------------------------------------------------
    
    # get the majority vote
    if NBResultLabels.count('positive') > NBResultLabels.count('negative'):
        #update database with count
        print("Overall Positive Sentiment")
        print("Positive Sentiment Percentage = " + str(100*NBResultLabels.count('positive')/len(NBResultLabels)) + "%")
    else: 
        print("Overall Negative Sentiment")
        print("Negative Sentiment Percentage = " + str(100*NBResultLabels.count('negative')/len(NBResultLabels)) + "%")
        

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
#building the model put this in a separate file
trainingData = buildTrainingSet(corpusFile)
preprocessedTrainingSet = processTweets(trainingData)
    
word_features = buildDictionary(preprocessedTrainingSet)
trainingFeatures = nltk.classify.apply_features(extract_features, preprocessedTrainingSet)
    
NBayesClassifier = nltk.NaiveBayesClassifier.train(trainingFeatures)
    
f = open('NB_Sentiment_Classifier.pickle', 'wb')
pickle.dump(NBayesClassifier, f)
f.close()
    
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

#fetched_tweets = api.search(q=trends[1], count=100, lang='en', tweet_mode='extended')

db=r"C:\sqlite\db\tweetSentiments.db"

main()
#TestClassifier()
  
