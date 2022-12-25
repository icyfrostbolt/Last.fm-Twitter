import tweepy, requests, json, time, os
from datetime import datetime, timedelta

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

last_fm_api = "09ea5c9e620811069d316508f2cf5035"
last_fm_secret = "eebb7cf8fb43d735127fcf6395f37f9b"

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
    message = f"{TWITTER_NAME}'s top {text} on {current_date.day}/{current_date.month}/{current_date.year}:"
    if len(ranked_list) > 5:
        for a in range(5):
            message = message + f"\n{a+1:}. {ranked_list[a][0]} - {ranked_list[a][1]} plays"
    else:
        for a in range(len(ranked_list)):
            message = message + f"\n{a+1:}. {ranked_list[a][0]} - {ranked_list[a][1]} plays"
    print(message)
    twitter.create_tweet(text=message)

def time_chart(year,month,day):
    global current_date, play_count_artist, play_count_album, play_count_song
    current_date = datetime(year,month,day)
    play_count_artist = {}
    play_count_album = {}
    play_count_song = {}

def rank():
   ranked_artists = sorted(play_count_artist.items(), key=lambda x: x[1], reverse=True)
   rank_tweeter(ranked_artists,"artists")
   ranked_albums = sorted(play_count_album.items(), key=lambda x: x[1], reverse=True)
   rank_tweeter(ranked_albums,"albums")
   ranked_songs = sorted(play_count_song.items(), key=lambda x: x[1], reverse=True)
   rank_tweeter(ranked_songs,"songs")

def update_song(track):
    if track['artist']['#text'] in play_count_artist:
        play_count_artist[track['artist']['#text']] += 1
    else:
        play_count_artist[track['artist']['#text']] = 1
    if f"{track['album']['#text']} - {track['artist']['#text']}" in play_count_album:
        play_count_album[f"{track['album']['#text']} - {track['artist']['#text']}"] += 1
    else:
        play_count_album[f"{track['album']['#text']} - {track['artist']['#text']}"] = 1
    if f"{track['name']} - {track['artist']['#text']}" in play_count_song:
        play_count_song[f"{track['name']} - {track['artist']['#text']}"] += 1
    else:
        play_count_song[f"{track['name']} - {track['artist']['#text']}"] = 1

def undo_latest(track):
    play_count_artist[track['artist']['#text']] -= 1
    play_count_album[f"{track['album']['#text']} - {track['artist']['#text']}"] -= 1
    play_count_song[f"{track['name']} - {track['artist']['#text']}"] -= 1

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
  tweeted = False
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
              # make it capable of looping in this json while it goes through the tracks
              tracks.append([[f"{t['name']} by {t['artist']['#text']}",[t['date']['#text'].split()],[t['image'][3]['#text']],[t]]]) # the number between ['image] and ['text] represents size
        # splits hour and minutes
        tracks[-1][-1][1][0][3] = tracks[-1][-1][1][0][3].split(":")
        for z in tracks[-1][-1][1][0][3]:
         tracks[-1][-1][1][0].append(z)
        tracks[-1][-1][1][0].remove(tracks[-1][-1][1][0][3])
        page_num -= 1
      except:
        pass
    for s in reversed(tracks):
      update_song(s[-1][3][0])
      # converts month abbreviation name into number
      monthname = s[-1][1][0][1]
      try:
        s[-1][1][0][1] = datetime.strptime(monthname, '%b').month
      except:
        break
      s[-1][1][0][2] = s[-1][1][0][2].strip(",")
      if most_recent == "":
        # Requests most recent tweets from a users timeline
        tweets = twitter.get_users_tweets(id=user_id,max_results=20)
        find_valid_tweet = False
        current_tweet = 0
        while find_valid_tweet == False:
          try: #adapt tis to find the most recent one that fits in case sharing with multipel programs
            tweets = str(tweets[0][current_tweet])
            most_recent = datetime(int(tweets[-28:-24]),int(tweets[-31:-29]),int(tweets[-34:-32]),int(tweets[-43:-41]),int(tweets[-40:-38]),0,0)
            time_chart(most_recent.year,most_recent.month,most_recent.day)
          except:
            if ":" in s[-1][1][0]:
              s[-1][1][0] = s[-1][1][0].split(":")
            date_data = s[-1][1][0]
            most_recent = datetime(int(date_data[2]), int(date_data[1]), int(date_data[0]), int(date_data[3]), int(date_data[4]), 0, 0)
            time_chart(most_recent.year, most_recent.month, most_recent.day)
            current_tweet += 1
            if most_recent == "":
              date_data = s[0][1][0]
              most_recent = datetime(int(date_data[2]),int(date_data[1]),int(date_data[0]),int(date_data[3]),int(date_data[4]),0,0)
              time_chart(most_recent.year, most_recent.month, most_recent.day)
              print(current_date)
          find_valid_tweet = True
      date_data = s[-1][1][0]
      try:
        print(date_data[4]) # if there is a 4th index it doesn't need to be split
      except:
        date_data[3] = date_data[3].split(":")
        date_data.append(date_data[3][1])
        date_data[3] = date_data[3][0]
      current_time = datetime(int(date_data[2]),int(date_data[1]),int(date_data[0]),int(date_data[3]),int(date_data[4]),0,0)
      if current_time > most_recent:
        most_recent = current_time
        if most_recent >= current_date + timedelta(days = 1):
            if tweeted:
                undo_latest(s[-1][3][0])
                rank()
                updated_most_recent = most_recent + timedelta(days = 1)
                time_chart(updated_most_recent.year, updated_most_recent.month, updated_most_recent.day)
        message = f"Listened to {s[0][0]} at {s[-1][1][0][3]}:{s[-1][1][0][4]} on {s[-1][1][0][0]}/{s[-1][1][0][1]}/{s[-1][1][0][2]}"
        tweet_image(s[0][2][0], message)
        print("Tweeted: %s" % message)
        tweeted = True
        time.sleep(1)
    if noerr:
      work = True