from googleapiclient.discovery import build

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pandas as pd
import demoji
from langdetect import detect
import re  
from tqdm import tqdm
import os
from flask import Flask, jsonify, json, request, render_template


import requests
import json
app = Flask(__name__)

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3' 

@app.route("/")
def index():
    res = {'check':'sahi h','data':{}}
    return render_template('index.html', r = res)

def get_authenticated_service():
  flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
  credentials = flow.run_console()
  return build(API_SERVICE_NAME, API_VERSION, credentials = credentials)

@app.route("/post",methods = ['POST','GET'])
def extract_data():

    if request.method == 'POST':

        empty = [" "]

        
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        service = get_authenticated_service()
    
        data = request.get_json()
        string = request.form.get('input_text')

        print("VALUE OF STRING ",string)

        # youTubeApiKey="AIzaSyCoBcCAxIGkTf5WKxAiXJu48APdyQjqU0I"
        # youtube=build('youtube','v3',developerKey=youTubeApiKey)
        query = "Sia - Cheap Thrills (Lyric Video) ft. Sean Paul"
        
        query_results = service.search().list(part = 'snippet',q = string,
                                      order = 'relevance', 
                                      type = 'video',
                                      relevanceLanguage = 'en',
                                      safeSearch = 'moderate').execute()
        

        video_id = []
        channel = []
        video_title = []
        video_desc = []

        for item in query_results['items']:
            video_id.append(item['id']['videoId'])
            channel.append(item['snippet']['channelTitle'])
            video_title.append(item['snippet']['title'])
            video_desc.append(item['snippet']['description'])

        channelTitle = query_results['items'][0]['snippet']['channelTitle']
    
        
        video_id = video_id[0]
        channel = channel[0]
        video_title = video_title[0]
        video_desc = video_desc[0]

        video_thumbnail = query_results['items'][0]['snippet']['thumbnails']['high']['url']

        ## CHANNELSTATS

        channelId = query_results['items'][0]['snippet']['channelId']
        stats = service.channels().list(part="statistics", id = channelId).execute()
        TotalSubscribers = stats['items'][0]['statistics']['subscriberCount']
        print(TotalSubscribers)

        ## VIDEOSTATS

        res = service.videos().list(id=video_id,part='statistics').execute()
        VideoViews = res['items'][0]['statistics']['viewCount']
        TotalLikes = res['items'][0]['statistics']['likeCount']
        TotalComments = res['items'][0]['statistics']['commentCount']

        
        video_id_pop = []
        channel_pop = []
        video_title_pop = []
        video_desc_pop = []
        comments_pop = []
        comment_id_pop = []
        reply_count_pop = []
        like_count_pop = []

        

        response = service.commentThreads().list(
                        part = 'snippet',
                        videoId = video_id,
                        maxResults = 100, # Only take top 100 comments...
                        order = 'relevance', #... ranked on relevance
                        textFormat = 'plainText',
                        ).execute()
        
        comments_temp = []
        comment_id_temp = []
        reply_count_temp = []
        like_count_temp = []

        for item in response['items']:
            comments_temp.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
            comment_id_temp.append(item['snippet']['topLevelComment']['id'])
            reply_count_temp.append(item['snippet']['totalReplyCount'])
            like_count_temp.append(item['snippet']['topLevelComment']['snippet']['likeCount'])

        comments_pop.extend(comments_temp)
        comment_id_pop.extend(comment_id_temp)
        reply_count_pop.extend(reply_count_temp)
        like_count_pop.extend(like_count_temp)
        
        video_id_pop.extend(video_id*len(comments_temp))
        channel_pop.extend(channel*len(comments_temp))
        video_title_pop.extend(video_title*len(comments_temp))
        video_desc_pop.extend(video_desc*len(comments_temp))
        
      
            
        query_pop = [query] * len(video_id_pop)

        # print("Comments", comments_pop)



        # snippets = youtube.search().list(part = "snippet", type = "channel",
                                            # q = string).execute()
        
        # channelId = snippets['items'][0]['snippet']['channelId']
        # channel_Name = snippets['items'][0]['snippet']['title']
        # description_channel = snippets['items'][0]['snippet']['description']

        # stats = youtube.channels().list(part="statistics",
        #                                  id = channelId).execute()

    
       

        # # Subscribers on the channel
        # total_subscribers = stats['items'][0]['statistics']['subscriberCount']
        # videos_uploaded = stats['items'][0]['statistics']['videoCount']
        # total_views = stats['items'][0]['statistics']['viewCount']

        # print("Name of Channel is::"+snippets['items'][0]['snippet']['title'])

        # print("\nThe Channel is published on::"+ snippets['items'][0]['snippet']['publishedAt'])

        # print("\nThe description of channel is::"+snippets['items'][0]['snippet']['description'])
        
        d = {}
        d["Channel_Name"] = channelTitle
        # d["Published_Date"] =  
        d["Video_Title"] = video_title
        d["Video_Description"] = video_desc
        d["Top_Comments"] = comments_pop
        d['Video_thumbnail'] = video_thumbnail
        d["Subscribers"] = TotalSubscribers
        d["Total_Views"] = VideoViews
        d["Total_Likes"] = TotalLikes
        d["Total_comments"] = TotalComments
        
        print(d)
        return render_template('index.html', r = {'old_data:':string,'data':d})
    else:
        return "ERROR IN POST REQUEST"

if __name__ == "__main__":
    app.run()