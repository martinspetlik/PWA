from mongoengine import *
from datetime import datetime
from server.models.user import User
from server.models.conversation import Conversation


class Message(Document):
    text = StringField(required=True, max_length=500)
    author = ReferenceField(User, required=True)
    conversation = ReferenceField(Conversation, required=True)
    date_created = DateTimeField(default=datetime.utcnow)