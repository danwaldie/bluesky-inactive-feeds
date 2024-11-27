#!/usr/bin/env python3
# YOU MUST INSTALL ATPROTO SDK
# pip3 install atproto

from atproto import Client, models
from dotenv import load_dotenv
import os
load_dotenv()

# YOUR bluesky handle
# Ex: user.bsky.social
HANDLE: str = os.getenv('HANDLE')

# YOUR bluesky password, or preferably an App Password (found in your client settings)
# Ex: abcd-1234-efgh-5678
PASSWORD: str = os.getenv('APP_PASSWORD')

# The hostname of the server where feed server will be hosted
# Ex: feed.bsky.dev
HOSTNAME: str = os.getenv('HOSTNAME')

# For each feed period (7d, 30d, 120d), run with these values:

# 7 days
RECORD_NAME = 'inactive-7d'
DISPLAY_NAME = 'Inactive (7 days)'
DESCRIPTION = 'Last posts from users who haven\'t posted in the past week'

# 30 days
RECORD_NAME = 'inactive-30d'
DISPLAY_NAME = 'Inactive (30 days)'
DESCRIPTION = 'Last posts from users who haven\'t posted in the past month'

# 120 days
RECORD_NAME = 'inactive-120d'
DISPLAY_NAME = 'Inactive (120 days)'
DESCRIPTION = 'Last posts from users who haven\'t posted in the past 4 months'

# (Optional) The path to an image to be used as your feed's avatar
# Ex: ./path/to/avatar.jpeg
AVATAR_PATH: str = ''

# (Optional). Only use this if you want a service did different from did:web
SERVICE_DID: str = ''


# -------------------------------------
# NO NEED TO TOUCH ANYTHING BELOW HERE
# -------------------------------------


def main():
    client = Client()
    client.login(HANDLE, PASSWORD)

    feed_did = SERVICE_DID
    if not feed_did:
        feed_did = f'did:web:{HOSTNAME}'

    avatar_blob = None
    if AVATAR_PATH:
        with open(AVATAR_PATH, 'rb') as f:
            avatar_data = f.read()
            avatar_blob = client.upload_blob(avatar_data).blob

    response = client.com.atproto.repo.put_record(models.ComAtprotoRepoPutRecord.Data(
        repo=client.me.did,
        collection=models.ids.AppBskyFeedGenerator,
        rkey=RECORD_NAME,
        record=models.AppBskyFeedGenerator.Record(
            did=feed_did,
            display_name=DISPLAY_NAME,
            description=DESCRIPTION,
            avatar=avatar_blob,
            created_at=client.get_current_time_iso(),
        )
    ))

    print('Successfully published!')
    print('Feed URI (put in "WHATS_ALF_URI" env var):', response.uri)


if __name__ == '__main__':
    main()
