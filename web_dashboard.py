import streamlit as st
import requests
import time
import webbrowser
import pickle
import os
import pandas as pd

from decouple import config
from topicmapping import topicmapping as tm

# Fetching a youtube video title using youtube API
def youtube_api_video_metadata(VID):
    video_meta_data = {
        'title': '',
        'description': '',
        'categoryID': '',
        'thumbnails': '',
        'tags': '',
        'channelTitle': ''
    }
    #Youtube Comment Tread API config
    API_KEY = YOUTUBE_API_KEY # Use your youtube data API key
    VideoID = VID
    
    URL = "https://www.googleapis.com/youtube/v3/videos?part=snippet&id="+VideoID+"&key="+API_KEY+""
    
    response = requests.get(URL)

    # Case 1
    err = ""
    if response.status_code == 200:
        json_data = response.json()
        if (len(json_data['items']) !=0):
            for item in json_data['items']:
                #st.code(item['snippet'])
                if 'title' in item['snippet']:
                    video_meta_data['title'] = item['snippet']['title']
                if 'description' in item['snippet']:
                    video_meta_data['description'] = item['snippet']['description']
                if 'thumbnails' in item['snippet']:
                    video_meta_data['thumbnails'] = item['snippet']['thumbnails']['standard']['url']
                if 'categoryId' in item['snippet']:
                    video_meta_data['categoryID'] = item['snippet']['categoryId']
                if 'channelTitle' in item['snippet']:
                    video_meta_data['channelTitle'] = item['snippet']['channelTitle']
                if 'tags' in item['snippet']:
                    video_meta_data['tags'] = item['snippet']['tags']
    else:
        err = response.status_code
    return video_meta_data, err


# Fetching a youtube video comments using youtube API
def youtube_api_comment(VID):
    comment_data = []
    #Youtube Comment Tread API config
    API_KEY = config('YOUTUBE_API_KEY') # Use your youtube data API key
    VideoID = VID

    URL = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&key="+API_KEY+"&videoId="+VideoID+"&maxResults=100"

    response = requests.get(URL)
    page = 2
    
    # Case 1
    err = ""
    with st.spinner('Fetching comments...'):
        if response.status_code == 200:
            json_data = response.json()
            for index, item in enumerate(json_data['items']):
                comment_data.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])

            while('nextPageToken' in json_data):
                #print('Fetching more comments from page {}..'.format(page))
                URL = "https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&key="+API_KEY+"&videoId="+VideoID+"&maxResults=100&&pageToken="+json_data['nextPageToken']
                response = requests.get(URL)
                if response.status_code == 200:
                    json_data = response.json()
                    for index, item in enumerate(json_data['items']):
                        comment_data.append(item['snippet']['topLevelComment']['snippet']['textDisplay'])
                    page+=1
        else:
            err = response.status_code
    return comment_data, err

def side_panel():
    st.sidebar.image('logo.png', width=280)
    menu = st.sidebar.radio(
        "Select Demo",
        ('YouTube Video','Sentiment Analysis', 'Topic Modelling', 'About'))
    return menu

def main_panel(menu):
    switcher = { 
        'Sentiment Analysis': sentiment_analysis_page, 
        'Topic Modelling': topic_modelling_page, 
        'YouTube Video': video_details_page,
        'About': about_page, 
    } 
    switcher[menu]()
    
def video_details_page():
    st.title("Sentiment Analysis and Topic Modelling on YouTube Video's Comments")
    data = {'video_id': '', 'comments': '', 'video_meta_data': '', 'topics': ''}
    videourl_txtfield = st.empty()
    video_url = videourl_txtfield.text_input(label="YouTube Video URL", value="", key="txt_url")
    if not video_url:
        st.warning('Please input a youtube video URL.')
    btn_submit =  st.button(label="Submit")
    if btn_submit:
        video_id = parseURL(video_url)
        video_meta_data, err = youtube_api_video_metadata(video_id)
        if not err:
            comments, err = youtube_api_comment(video_id)
            if not err:
                display_video_metadata(video_meta_data)
                # dump result in pickle file
                f = open('store.pckl', 'wb')
                pickle.dump({'video_id': video_id, 'comments': comments, 'video_meta_data': video_meta_data, 'topics': ''}, f)
                f.close()
            else:
                st.error('Error: {}'.format(err))
        else: 
            st.error('Error: {}'.format(err))
    else:
        if (os.path.isfile('store.pckl') == True):
            f = open('store.pckl', 'rb')
            data = pickle.load(f)
            f.close()
            if data:
                display_video_metadata(data['video_meta_data'])

def sentiment_analysis_page():
    st.title("Sentiment Analysis Result on YouTube Video's Comments")
    # Create a text element and let the reader know the data is loading.
    data_load_state = st.text('Loading data...')
    # Load data into the dataframe.
    data = load_data("sample_comments.csv")
    # Notify the reader that the data was successfully loaded.
    data_load_state.text("Done! (using st.cache)")
    st.dataframe(data)

@st.cache
def load_data(filename):
    df = pd.read_csv(filename)
    return df

def topic_modelling_page():
    st.title("Topic Modelling Result on YouTube Video's Comments")
    if (os.path.isfile('store.pckl') == True):
            f = open('store.pckl', 'rb')
            data = pickle.load(f)
            f.close()
            if data:
                if(data['topics'] == ''):
                    df = pd.DataFrame(data['comments'], columns=['Comments'])
                    topics = tm.fetch_topic(df)
                    df.to_csv('sample_comments.csv', index=False)
                    
                    #Dump the topics
                    f = open('store.pckl', 'wb')
                    pickle.dump({'video_id': data['video_id'], 'comments': data['comments'], 'video_meta_data': data['video_meta_data'], 'topics': topics}, f)
                    f.close()
                    
                    st.header('Topics')
                    display_topics(topics)
                else:
                    display_topics(data['topics'])
            else:
                st.error("Please, fetch the comments first, select YouTube Video option from the menu.")
                
def display_topics(topics):
    for topic in topics:
        st.markdown("```{}```".format(topic))

def about_page():
    st.title("About Page")
    
def parseURL(URL):
    video_id = ""
    if('v=' in URL):
        video_id = URL.split('v=')[1].split('&')[0]
    return video_id

def display_video_metadata(video_meta_data):
   # st.code(video_meta_data)
    btn_clear = st.empty()
    video_header = st.empty()
    video_image = st.empty()
    video_details = st.empty()
    video_info = st.empty()
    if  video_meta_data:
        if btn_clear.button(label="Clear all"):
            f = open('store.pckl', 'wb')
            pickle.dump({}, f)
            f.close()
        else:
            video_header.header(video_meta_data['title'])
            video_image.image(video_meta_data['thumbnails'])
            if video_details.checkbox('Show video description'):
               video_info.info(video_meta_data['description'])


if __name__ == '__main__':
    menu = side_panel()
    main_panel(menu)


