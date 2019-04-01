import praw
import re
import os
import requests as request
import datetime
from tqdm import tqdm


def create_folder():

    """create our folder for the day"""

    try: #make daily folder if it already exists continue
        os.makedirs(f'highlight_bot_{today}', exist_ok=False) 
        folder = os.path.dirname(os.path.realpath(f'highlight_bot_{today}'))
    except OSError:
        folder = os.path.dirname(os.path.realpath(f'highlight_bot_{today}'))

    return folder

def finder(folder, subreddit):

    """get our hightlights from r/nba and r/soccer top and hot"""

    list_of_pl = [] #list of our post links
    posts_scanned = [] # list of ids to avoid getting duplicate list_of_pl in hot and top
    post_names = [] #list of names for vid titles

    with open("posts_scanned.txt", "r") as f: #text file to keep history of downloads, so we never download same post twice
        posts_scanned = f.read()
        posts_scanned = posts_scanned.split("\n")
        posts_scanned = list(filter(None, posts_scanned))
    
    for submission in subreddit.top(time_filter='day',limit=40,):
        if re.search('streamable', submission.url) != None:
            if submission.id not in posts_scanned:
                post_title = submission.title
                post_link = submission.url
                posts_scanned.append(submission.id)#IDs for .txt
                list_of_pl.append(post_link)#streamable link from reddit post
                post_names.append(post_title)#post titles for video files
                
    for submission in subreddit.hot(limit = 30):
        if re.search('streamable', submission.url) != None:
            if submission.id not in posts_scanned:
                    post_title = submission.title
                    post_link = submission.url
                    list_of_pl.append(post_link)
                    post_names.append(post_title)

    with open("posts_scanned.txt", "w") as f: #write posts ids to our .txt
        for post_id in posts_scanned:
            f.write(post_id + "\n")

    sub_link_list = [] #index through links to get sublinks to pass to downloader
    for each in list_of_pl:
        sub_link_list.append(each[23::])
    
    master_tup = tuple(zip(post_names,sub_link_list)) #tuple of title and sublink for video file creation
    
    return master_tup

        
def get_vids(folder, sublinks):

    """download highlights into daily folder per our reddit findings"""
    
    for title, content in tqdm(sublinks): #go through tuple each sublink, download and save to our new directory under reddit title
        
        try:
            
            url = (f'https://api.streamable.com/videos/{content}')
            user = ('wmacleod@flowroute.com')
            password = ('wmacleod0')
            response = request.get(url, auth=(user, password), stream = True)
            url_str = str(response.content)
            url_search=url_str[70:165]#index of response of our actual .mp4
            url_search=('https:'+url_search)
            filename = f'{title[0:250]}.mp4' #max filename length for windows/mac
            r = request.get(url_search, auth=(user, password), stream = True)
            with open(os.path.join(f'highlight_bot_{today}', f'{filename}'), 'wb') as f:
                print('Downloading and writing')
                for chunk in r.iter_content(chunk_size=1024*10):#download in chunks
                    f.write(chunk)
                    f.flush()

        except FileNotFoundError: #video source has been taken down but reddit post still exists
            print('FileNotFoundError')
            pass
        except: #catch 'InvalidUrl' requests error that is very rarely raised
            url_search = ('http://'+url_search)

if __name__ == "__main__":

    reddit = praw.Reddit('bot1')
    nba_subreddit = reddit.subreddit("nba")
    soccer_subreddit = reddit.subreddit("soccer")
    today = datetime.datetime.today().strftime('%m-%d-%Y')



    folder = create_folder()
    
    sublinks = finder(folder, nba_subreddit)
    get_vids(folder,sublinks)

    sublinks = finder(folder, soccer_subreddit)
    get_vids(folder,sublinks)