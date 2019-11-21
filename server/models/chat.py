from mongoengine import *
import mongoengine_goodjson as gj
from server.models.user import User
from datetime import datetime


class Chat(gj.Document):
    members = ListField(gj.FollowReferenceField(User))
    date_created = DateTimeField(default=datetime.utcnow)
    last_message_date = DateTimeField()


class Chat_db():

    @staticmethod
    def create_new(members):
        chats_same_members = Chat.objects(members=members)

        print("chats same members ", chats_same_members)
        if not chats_same_members:
            Chat(members).save()
        else:
            raise Exception("Chat with same members already exists")


