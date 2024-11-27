from collections import defaultdict
from datetime import datetime

from atproto import models

from server.logger import logger
from server.database import db, Post, User


def operations_callback(ops: defaultdict) -> None:
    # Here we can filter, process, run ML classification, etc.
    # After our feed alg we can save posts into our DB
    # Also, we should process deleted posts to remove them from our DB and keep it in sync

    # for example, let's create our custom feed that will contain all posts that contains alf related text

    posts_to_create = []
    for created_post in ops[models.ids.AppBskyFeedPost]['created']:
        author = created_post['author']
        record = created_post['record']

        # print all texts just as demo that data stream works
        post_with_images = isinstance(record.embed, models.AppBskyEmbedImages.Main)
        inlined_text = record.text.replace('\n', ' ')
        logger.info(
            f'NEW POST '
            f'[CREATED_AT={record.created_at}]'
            f'[AUTHOR={author}]'
            f'[WITH_IMAGE={post_with_images}]'
            f': {inlined_text}'
        )

        # only alf-related posts
        if 'alf' in record.text.lower():
            reply_root = reply_parent = None
            if record.reply:
                reply_root = record.reply.root.uri
                reply_parent = record.reply.parent.uri

            post_dict = {
                'uri': created_post['uri'],
                'cid': created_post['cid'],
                'reply_parent': reply_parent,
                'reply_root': reply_root,
            }
            posts_to_create.append(post_dict)

    posts_to_delete = ops[models.ids.AppBskyFeedPost]['deleted']
    if posts_to_delete:
        post_uris_to_delete = [post['uri'] for post in posts_to_delete]
        Post.delete().where(Post.uri.in_(post_uris_to_delete))
        logger.info(f'Deleted from feed: {len(post_uris_to_delete)}')

    if posts_to_create:
        with db.atomic():
            for post_dict in posts_to_create:
                Post.create(**post_dict)
        logger.info(f'Added to feed: {len(posts_to_create)}')

    # Track users and their latest posts
    users_to_update = []
    for created_post in ops[models.ids.AppBskyFeedPost]['created']:
        author_did = created_post['author']
        record = created_post['record']
        post_time = datetime.fromisoformat(record.created_at.replace('Z', '+00:00'))
        
        # Get or prepare new user record
        user, created = User.get_or_create(
            did=author_did,
            defaults={
                'handle': None,
                'last_post_time': post_time,
                'last_post_uri': created_post['uri'],
                'last_post_cid': created_post['cid']
            }
        )
        
        # Update if this is a newer post
        if not created and (not user.last_post_time or post_time > user.last_post_time):
            user.last_post_time = post_time
            user.last_post_uri = created_post['uri']
            user.last_post_cid = created_post['cid']
            users_to_update.append(user)

    # Batch update users
    if users_to_update:
        with db.atomic():
            for user in users_to_update:
                user.save()
