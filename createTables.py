# -*- coding: utf-8 -*-
"""
Created on Fri Jan  1 17:34:42 2021

@author: Tyler
"""

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

def main():
    database = r"C:\sqlite\db\tweetSentiments.db"    
    
    #create database connection
    conn = create_connection(database)
    
    #create tables
    if conn is not None:
        #create trends table
        create_table(conn,""" CREATE TABLE IF NOT EXISTS trends(
            trend text NOT NULL,
            collected_on text NOT NULL,
            positive_tweets integer,
            negative_tweets integer,
            neutral_tweets integer,           
            PRIMARY KEY(trend, collected_on)
            );""")      
                      
        #create tweets table
        create_table(conn,""" CREATE TABLE IF NOT EXISTS tweets(
            id integer NOT NULL,
            trend text NOT NULL,
            collected_on text NOT NULL,
            sentiment text,
            FOREIGN KEY (trend) REFERENCES trends(trend )
            FOREIGN KEY (collected_on) REFERENCES trends(collected_on)
            PRIMARY KEY (id)
            );""")      
        
    else:
        print("Error: Unable to connect to database")

            

if __name__ == '__main__':
    main()