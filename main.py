import tweepy, requests, json, time, os
from datetime import datetime

#twitter

bearer_token = #twitter bearer token
access_token = #twitter access token
access_token_secret = #twitter access token secret
consumer_key = #twitter consumer key
consumer_secret = #twitter consumer secret

user_id = # twitter user id you want to post from

twitter = tweepy.Client(bearer_token=bearer_token,consumer_key=consumer_key,consumer_secret=consumer_secret,access_token=access_token,access_token_secret=access_token_secret)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#last.fm

last_fm_api = # last fm api key
last_fm_secret = # last fm api secret

def lastfm_get(payload):
    global page_num
    # define headers and URL
    headers = {'user-agent': USER}
    url = 'https://ws.audioscrobbler.com/2.0/'

    # Add API key and format to the payload
    payload['api_key'] = last_fm_api
    payload['format'] = 'json'
    payload['user'] = USER
    payload['limit'] = 200
    payload['page'] = page_num

    response = requests.get(url, headers=headers, params=payload)
    return response

def jprint(obj):
    #create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    #print(text)

most_recent = ""

def tweet_image(url, message):
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
        media = api.media_upload("temp.jpg")
        twitter.create_tweet(media_ids=[str(media.media_id)], text=message)
        os.remove(filename)
    else:
        print("Unable to download image")

def rank_tweeter(ranked_list,text):
    message = f"Top {text} for {TWITTER_NAME}'s last 1000 listens:"
    if len(ranked_list) > 5:
        for a in range(5):
            message = message + f"\n{a+1:}. {ranked_list[a][0]} - {ranked_list[a][1]} plays"
            # call to find image album.getInfo, artist.getInfo, track.getInfo then add them to the tweet
    else:
        for a in range(len(ranked_list)):
            message = message + f"\n{a+1:}. {ranked_list[a][0]} - {ranked_list[a][1]} plays"
            # call to find image
    twitter.create_tweet(text=message)

def rank():
   ranked_artists = sorted(play_count_artist.items(), key=lambda x: x[1], reverse=True)
   rank_tweeter(ranked_artists,"artists")
   ranked_albums = sorted(play_count_album.items(), key=lambda x: x[1], reverse=True)
   rank_tweeter(ranked_albums,"albums")
   ranked_songs = sorted(play_count_song.items(), key=lambda x: x[1], reverse=True)
   rank_tweeter(ranked_songs,"songs")

usernames = [] #lastfm username of people who you want to get songs listened to from, organized in a tuple with (name of person, name to appear on twitter)

for users in usernames: 
  USER = users[0]
  TWITTER_NAME = users[1]
  counter = 0
  page_num = 5
  play_count_artist = {}
  play_count_album = {}
  play_count_song = {}
  work = False
  while work == False:
    while page_num > 0:
      print(page_num)
      tracks = []
      r = lastfm_get({
      'method': 'user.getRecentTracks'
    })
      time.sleep(1)
      jprint(r.json())
      try: # This stops it from breaking because of no recenttracks key
        noerr = True
        for t in r.json()['recenttracks']['track']:
            if not "@attr" in t:
                tracks.append([[f"{t['name']} by {t['artist']['#text']}",[t['date']['#text'].split()],[t['image'][3]['#text']]]]) # the number between ['image] and ['text] represents size
                if t['artist']['#text'] in play_count_artist:
                    play_count_artist[t['artist']['#text']] += 1
                else:
                    play_count_artist[t['artist']['#text']] = 0
                if f"{t['album']['#text']} - {t['artist']['#text']}" in play_count_album:
                    play_count_album[f"{t['album']['#text']} - {t['artist']['#text']}"] += 1
                else:
                    play_count_album[f"{t['album']['#text']} - {t['artist']['#text']}"] = 0
                if f"{t['name']} - {t['artist']['#text']}" in play_count_song:
                    play_count_song[f"{t['name']} - {t['artist']['#text']}"] += 1
                else:
                    play_count_song[f"{t['name']} - {t['artist']['#text']}"] = 0
        # splits hour and minutes
        tracks[-1][-1][1][0][3] = tracks[-1][-1][1][0][3].split(":")
        for z in tracks[-1][-1][1][0][3]:
            tracks[-1][-1][1][0].append(z)
        tracks[-1][-1][1][0].remove(tracks[-1][-1][1][0][3])
        page_num -= 1
      except:
        pass
    for s in reversed(tracks):
      # converts month abbreviation name into number
      monthname = s[-1][1][0][1]
      try:
          s[-1][1][0][1] = datetime.strptime(monthname, '%b').month
      except:
          break
      s[-1][1][0][2] = s[-1][1][0][2].strip(",")
      if most_recent == "":
        # Requests most recent tweets from a users timeline
        tweets = twitter.get_users_tweets(id=user_id,max_results=5)
        try: #adapt tis to find the most recent one that fits in case sharing with multipel programs   
          tweets = str(tweets[0][3])
          most_recent = datetime(int(tweets[-28:-24]),int(tweets[-31:-29]),int(tweets[-34:-32]),int(tweets[-43:-41]),int(tweets[-40:-38]),0,0)
        except:
          if ":" in s[-1][1][0]:
            s[-1][1][0] = s[-1][1][0].split(":")
          date_data = s[-1][1][0]
          most_recent = datetime(int(date_data[2]), int(date_data[1]), int(date_data[0]), int(date_data[3]), int(date_data[4]), 0, 0)
          if most_recent == "":
              date_data = s[0][1][0]
              most_recent = datetime(int(date_data[2]),int(date_data[1]),int(date_data[0]),int(date_data[3]),int(date_data[4]),0,0)
      date_data = s[-1][1][0]
      try:
        print(date_data[4]) # if there is a 4th index it doesn't need to be split
      except:
        date_data[3] = date_data[3].split(":")
        date_data.append(date_data[3][1])
        date_data[3] = date_data[3][0]
      current_time = datetime(int(date_data[2]),int(date_data[1]),int(date_data[0]),int(date_data[3]),int(date_data[4]),0,0)
      if current_time > most_recent:
        message = f"{TWITTER_NAME} listened to {s[0][0]} at {s[-1][1][0][3]}:{s[-1][1][0][4]} on {s[-1][1][0][0]}/{s[-1][1][0][1]}/{s[-1][1][0][2]}"
        tweet_image(s[0][2][0], message)
        print("Tweeted: %s" % message)
        most_recent = current_time
        time.sleep(1)
    if noerr:
      rank()
      work = True