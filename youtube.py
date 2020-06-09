from googleapiclient.discovery import build
from flask import Flask, jsonify, json, request, render_template


import requests
import json
app = Flask(__name__)

@app.route("/")
def index():
    res = {'check':'sahi h','data':{}}
    return render_template('index.html', r = res)


@app.route("/post",methods = ['POST','GET'])
def extract_data():

    if request.method == 'POST':

        empty = [" "]
        data = request.get_json()
        string = request.form.get('input_text')


        youTubeApiKey="AIzaSyCoBcCAxIGkTf5WKxAiXJu48APdyQjqU0I"
        youtube=build('youtube','v3',developerKey=youTubeApiKey)

        snippets = youtube.search().list(part = "snippet", type = "channel",
                                            q = string).execute()
        
        channelId = snippets['items'][0]['snippet']['channelId']
        channel_Name = snippets['items'][0]['snippet']['title']
        description_channel = snippets['items'][0]['snippet']['description']

        stats = youtube.channels().list(part="statistics",
                                         id = channelId).execute()

    
       

        # Subscribers on the channel
        total_subscribers = stats['items'][0]['statistics']['subscriberCount']
        videos_uploaded = stats['items'][0]['statistics']['videoCount']
        total_views = stats['items'][0]['statistics']['viewCount']

        print("Name of Channel is::"+snippets['items'][0]['snippet']['title'])

        print("\nThe Channel is published on::"+ snippets['items'][0]['snippet']['publishedAt'])

        print("\nThe description of channel is::"+snippets['items'][0]['snippet']['description'])
        
        d = {}
        d["Channel_Name"] = channel_Name
        # d["Published_Date"] =  
        d["Video_Description"] = description_channel
        d["Subscribers"] = total_subscribers
        d["Total_Videos"] = videos_uploaded
        d["Total_Views"] = total_views
        print(d)
        return render_template('index.html', r = {'old_data:':string,'data':d})
    else:
        return "ERROR IN POST REQUEST"

if __name__ == "__main__":
    app.run()