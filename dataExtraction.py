import praw
import urllib.request
from datetime import datetime
from time import sleep
import json

def get_reddit(credfile = 'reddit_credentials.json'):
    '''
    read credentials from file  and return the parsed json data.
    '''
    with open(credfile) as json_data:
        cred = json.load(json_data)
    reddit = praw.Reddit(client_id= cred['client_id'],
                         client_secret= cred ['client_secret'],
                         user_agent= cred['user_agent'])
    return reddit

def get_data(reddit=None,sub='funny', maxposts=10):
    '''
    Extracts one datapoint consisting of maxposts posts, from the targeted sub.
    For each post, it extracts:
    -number of upvotes
    -number of Comments
    -thumbnail
    -age in minutes   
    -title
    -subreddit
      '''
    if not reddit:
        reddit = get_reddit()

    limit_read = maxposts + 2 
    submissions = reddit.subreddit(sub).new(limit=limit_read)
    thumbnailsfolder = 'thumbnails/'
    data = { 'ups':[],'coms':[],'thumbs':[],'ages':[],'titles':[], 'subs':[]}

    for submission in submissions:
        if not submission.stickied:
            data['ups'].append(submission.ups)
            data['coms'].append(submission.num_comments)
            data['titles'].append(submission.title)
            age = datetime.now() - datetime.fromtimestamp(submission.created_utc)
            age = divmod(age.total_seconds(), 60)[0] #age is in minutes
            data['ages'].append(age)
            try :
                image_name = thumbnailsfolder + submission.name + '.jpg'
                image_url = submission.preview['images'][0]['resolutions'][0]['url']
                urllib.request.urlretrieve(image_url, image_name)
            except AttributeError:
                image_name = '_nopreview.png'
            data['thumbs'].append(image_name)
            data['subs'].append(submission.subreddit_name_prefixed) #useful for r/funny

    
    for d in data:
        data[d] = data[d][:maxposts]

    data['timestamp'] = datetime.now().strftime("%b %d %Y %H:%M:%S")
    data['sub'] = sub
    return data

def collect_data(sub='all',maxposts=10,interval_sec=6,duration_min=10,feedback=True,savefile=None):
    '''
    This module repeats the get_data function during the duration_min in minutes, at every interval_sec in seconds.
      Returns data_collec, a list of data from get_data.
    '''
    size = round((duration_min*60)/interval_sec)
    reddit = get_reddit()
    data_collec = []
    for n in range(size):
        data = get_data(reddit,sub,maxposts)
        data_collec.append(data)
        if feedback:
            print('{}/{} snapshot recorded on {}'.format(n+1,size,data['timestamp']))
        if savefile:
            with open(savefile, 'w') as f:
                json.dump(data_collec, f)
        if n!=size-1:
            sleep(interval_sec)
    return data_collec

def offset_timestamp(data,delta_hours):
    '''
    set the time stamp for data and offset for each data point
    Return one data point.
    '''
    from datetime import timedelta

    timestamp = datetime.strptime(data['timestamp'],"%b %d %Y %H:%M:%S")

    timestamp = timestamp + timedelta(hours=delta_hours)
    data['timestamp'] = timestamp.strftime("%b %d %Y %H:%M:%S")
    return data

if __name__ == '__main__':
    pass
