from mongoengine import *
from server.models.user import User
from datetime import datetime


class Conversation(Document):
    members = ListField(ReferenceField(User))
    date_created = DateTimeField(default=datetime.utcnow)
    last_message_date = DateTimeField()


