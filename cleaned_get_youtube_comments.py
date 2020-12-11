## BORROWED VERY HEAVILY FROM AND CREDIT TO:
## https://towardsdatascience.com/how-to-build-your-own-dataset-of-youtube-comments-39a1e57aade
## Ken Jee

import json
from csv import writer
from apiclient.discovery import build
import pandas as pd
import pickle
import urllib.request
import urllib


key = '<KEY>' #replace with your youtube data api key
videoId = '5cathmZFeXs'
videoId = 'bPiofmZGb8o'
# channelId = 'UC2UXDak6o7rBm23k3Vv5dww' # mine
# channelId = 'UCiT9RITQ9PW6BhXK0y2jaeg' # kens


def build_service():
    YOUTUBE_API_SERVICE_NAME = "youtube"
    YOUTUBE_API_VERSION = "v3"
    return build(YOUTUBE_API_SERVICE_NAME,
                 YOUTUBE_API_VERSION,
                 developerKey=key)


#2 configure function parameters for required variables to pass to service
def get_comments(part='snippet', 
                 maxResults=100, 
                 textFormat='plainText',
                 order='time',
                 allThreadsRelatedToChannelId=channelId,
                 # videoId=videoId,
                 csv_filename="tinas_comments"
                 ):

    #3 create empty lists to store desired information
    comments, commentsId, authorurls, authornames, repliesCount, likesCount, viewerRating, dates, vidIds, totalReplyCounts,vidTitles = [], [], [], [], [], [], [], [], [], [], []

    # build our service from path/to/apikey
    service = build_service()
    
    #4 make an API call using our service
    response = service.commentThreads().list(
        part=part,
        maxResults=maxResults,
        textFormat='plainText',
        order=order,
        # videoId=videoId
        allThreadsRelatedToChannelId=channelId
    ).execute()

    while response: # this loop will continue to run until you max out your quota

        for item in response['items']:
            #5 index item for desired data features
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_id = item['snippet']['topLevelComment']['id']
            reply_count = item['snippet']['totalReplyCount']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']
            authorurl = item['snippet']['topLevelComment']['snippet']['authorChannelUrl']
            authorname = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
            date = item['snippet']['topLevelComment']['snippet']['publishedAt']
            vidId = item['snippet']['topLevelComment']['snippet']['videoId']
            totalReplyCount = item['snippet']['totalReplyCount']
            vidTitle = get_vid_title(vidId)

            #6 append to lists
            comments.append(comment)
            commentsId.append(comment_id)
            repliesCount.append(reply_count)
            likesCount.append(like_count)
            authorurls.append(authorurl)
            authornames.append(authorname)
            dates.append(date)
            vidIds.append(vidId)
            totalReplyCounts.append(totalReplyCount)
            vidTitles.append(vidTitle)

        try:
            if 'nextPageToken' in response:
                response = service.commentThreads().list(
                    part=part,
                    maxResults=maxResults,
                    textFormat=textFormat,
                    order=order,
                    # videoId=videoId,
                    allThreadsRelatedToChannelId=channelId,
                    pageToken=response['nextPageToken']
                ).execute()
            else:
                break
        except: break

    #9 return our data of interest
    return {
        'comment': comments,
        'comment_id': commentsId,
        'author_url': authorurls,
        'author_name': authornames,
        'reply_count' : repliesCount,
        'like_count' : likesCount,
        'date': dates,
        'vidid': vidIds,
        'total_reply_counts': totalReplyCounts,
        'vid_title': vidTitles
    }


# vidid to table name
def get_vid_title(vidid):
    # VideoID = "LAUa5RDUvO4"
    params = {"format": "json", "url": "https://www.youtube.com/watch?v=%s" % vidid}
    url = "https://www.youtube.com/oembed"
    query_string = urllib.parse.urlencode(params)
    url = url + "?" + query_string

    with urllib.request.urlopen(url) as response:
        response_text = response.read()
        data = json.loads(response_text.decode())
        # print(data['title'])
        return data['title']

if __name__ == '__main__':
    tinas_comments = get_comments()
    df = pd.DataFrame(tinas_comments)
    print(df.shape)
    print(df.head())
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['just_date'] = df['date'].dt.date
    df.to_csv('./tinas_comments.csv')
