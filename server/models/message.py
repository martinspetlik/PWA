from mongoengine import *
import mongoengine_goodjson as gj
from datetime import datetime
from server.models.user import User
from server.models.chat import Chat


class Message(gj.Document):
    text = StringField(required=True, max_length=500)
    author = gj.FollowReferenceField(User, required=True)
    chat = ReferenceField(Chat, required=True)
    date_created = DateTimeField(default=datetime.utcnow)
