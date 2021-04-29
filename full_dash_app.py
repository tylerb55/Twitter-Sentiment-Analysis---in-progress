# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 11:03:12 2021

@author: Tyler
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import date
from collections import deque
import plotly.graph_objs as go
import random
import sqlite3
import pandas as pd
import webbrowser
from sentiment_analysis import one_term

db=r"C:\sqlite\db\tweetSentiments.db"

# Read sqlite query results into a pandas DataFrame
con = sqlite3.connect(db)
tweets = pd.read_sql_query("SELECT * FROM tweets", con)
trends = pd.read_sql_query("SELECT * FROM trends", con)
recurring = pd.read_sql_query("SELECT trend, COUNT(collected_on) FROM trends GROUP BY trend HAVING COUNT(collected_on)>1", con)
most_negative = trends.sort_values(by="negative_tweets", ascending=False).head()
most_positive = trends.sort_values(by="positive_tweets", ascending=False).head()
most_neutral = trends.sort_values(by="neutral_tweets", ascending=False).head()

con.close()

#one_term("amax")
#use event trends= one_term(input_data)
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def search_term(term):
    searchterm = trends.loc[trends['trend'] == term]
    if(term[0:1]=='#'):
        term = term.replace('#','')
        searchterm2 = trends.loc[trends['trend'] == term]
    else:
        term = "#"+term
        searchterm2 = trends.loc[trends['trend'] == term]
    if(searchterm.size!=0):
        return searchterm
    elif(searchterm2.size!=0):
        return searchterm2
    else:
        return searchterm

def by_day(date):
    searchdate = trends.loc[trends['collected_on'] == date]
    return searchdate

app = dash.Dash('Twitter Sentiment')

term = trends
day = trends

data_dict = {"Search Term":term,
"By Day": day,
"Most Positive": most_positive,
"Most Neutral":most_neutral,
"Most Negative":most_negative,
"Recurring":recurring}

app.layout = html.Div([
    html.Div([
        html.H2('Twitter Sentiment',),
        ]),
    html.Div([html.P('Enter Search Term:'),
    dcc.Input(id='search_term', value="", type="text"),html.Button('Search Twitter',id='add_term',n_clicks=0)], className="row"),
    html.Div([html.P('Enter day to search for:'),
    dcc.DatePickerSingle(id= 'search_day',date=date.today(),display_format="YYYY-MM-DD")],className="row"),
    dcc.Dropdown(id='twitter-data-name',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 value=['Search Term','By Day','Most Positive'],
                 multi=True
                 ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Interval(
        id='graph-update',
        interval=100),
    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})

@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('twitter-data-name', 'value')],
    [dash.dependencies.Input('graph-update', 'n_intervals')],
    [dash.dependencies.Input('search_term', 'value')],
    [dash.dependencies.Input('search_day', 'date')],
    [dash.dependencies.Input('add_term', 'n_clicks')]
    )
def update_graph(data_names,input_data,s_term,s_day):
    graphs = []
    #update_obd_values(times, term, day, most_positive, most_neutral, most_negative, throttle_pos)
    
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'
    
    for data_name in data_names:
        df=trends        
        if(data_name=="Search Term"):
            try:
                df = search_term(s_term)
            except:
                df.fillna(0)
            
            graphs.append(html.Div(dcc.Graph(
                id="searched",
                figure={
                    'data': [
                        {'x': df.collected_on, 'y': df.positive_tweets, 'type': 'bar', 'name': 'Positive Tweets'},
                        {'x': df.collected_on, 'y': df.negative_tweets, 'type': 'bar', 'name': 'Negative Tweets'},
                        {'x': df.collected_on, 'y': df.neutral_tweets, 'type': 'bar', 'name': 'Neutral Tweets'},
                    ],
                    'layout': {
                        'title': s_term
                    }
                })))
        elif(data_name=="By Day"):
            try:
                df = by_day(s_day)
            except:
                df.fillna(0)
            
            graphs.append(html.Div(dcc.Graph(
                id="day",
                figure={
                    'data': [
                        {'x': df.trend, 'y': df.positive_tweets, 'type': 'bar', 'name': 'Positive Tweets'},
                        {'x': df.trend, 'y': df.negative_tweets, 'type': 'bar', 'name': 'Negative Tweets'},
                        {'x': df.trend, 'y': df.neutral_tweets, 'type': 'bar', 'name': 'Neutral Tweets'},
                    ],
                    'layout': {
                        'title': s_day
                    }
                })))
        elif(data_name=="Recurring"):
            df=recurring
            graphs.append(html.Div(dcc.Graph(
                id="recurring",
                figure={
                    'data': [
                        {'x': df.trend, 'y': df[df.columns[1]], 'type': 'bar', 'name': 'Occurence'},
                    ],
                    'layout': {
                        'title': "Recurring Trends"
                    }
                })))
            
        else:
            df=data_dict[data_name]
            graphs.append(html.Div(dcc.Graph(
                id="most",
                figure={
                    'data': [
                        {'x': df.trend, 'y': df.positive_tweets, 'type': 'bar', 'name': 'Positive Tweets'},
                        {'x': df.trend, 'y': df.negative_tweets, 'type': 'bar', 'name': 'Negative Tweets'},
                        {'x': df.trend, 'y': df.neutral_tweets, 'type': 'bar', 'name': 'Neutral Tweets'},
                    ],
                    'layout': {
                        'title': data_name
                    }
                })))

    return graphs

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/')
    app.run_server(debug=True, use_reloader=False)