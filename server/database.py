from datetime import datetime

import peewee

db = peewee.SqliteDatabase('feed_database.db')


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Post(BaseModel):
    uri = peewee.CharField(index=True)
    cid = peewee.CharField()
    reply_parent = peewee.CharField(null=True, default=None)
    reply_root = peewee.CharField(null=True, default=None)
    indexed_at = peewee.DateTimeField(default=datetime.utcnow)


class SubscriptionState(BaseModel):
    service = peewee.CharField(unique=True)
    cursor = peewee.BigIntegerField()


class User(BaseModel):
    did = peewee.CharField(unique=True)  # User's DID
    handle = peewee.CharField(null=True)  # User's handle (for display)
    last_post_uri = peewee.CharField(null=True)
    last_post_cid = peewee.CharField(null=True)
    last_post_time = peewee.DateTimeField(null=True)
    indexed_at = peewee.DateTimeField(default=datetime.now)


if db.is_closed():
    db.connect()
    db.create_tables([Post, SubscriptionState, User])
