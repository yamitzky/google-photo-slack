import os
import time

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import requests

GOOGLE_TOKEN = os.environ['GOOGLE_TOKEN']
SLACK_TOKEN = os.environ['SLACK_TOKEN']
SLACK_CHANNEL = os.environ['SLACK_CHANNEL']

creds = Credentials(GOOGLE_TOKEN)
gp = build('photoslibrary', 'v1', credentials=creds)

posted = set()
fetched = False
while True:
    print('start...')
    albums = gp.sharedAlbums().list().execute()
    for album in albums['sharedAlbums'][:2]:
        print('Fetching', album['title'])
        items = gp.mediaItems().search(body={
            'albumId': album['id'],
        }).execute()
        for item in items['mediaItems']:
            id = item['id']
            if id not in posted:
                if fetched:
                    requests.post('https://slack.com/api/chat.postMessage', json={
                        'channel': SLACK_CHANNEL,
                        'text': f'New photo @ {album["title"]}',
                        'attachments': [{
                            'title': 'Display on Google Photo',
                            'image_url': item['baseUrl'],
                            'title_link': item['productUrl']
                        }]
                    }, headers={
                        'Authorization': f'Bearer {SLACK_TOKEN}'
                    })
                posted.add(id)
    fetched = True
    print('sleep...')
    time.sleep(60)
