from mongoengine import *
import mongoengine_goodjson as gj
from server.models.user import User
from datetime import datetime


class Chat(gj.Document):
    title = StringField(max_length=25)
    members = ListField(gj.FollowReferenceField(User))
    date_created = DateTimeField(default=datetime.utcnow)
    last_message_date = DateTimeField()


class ChatCreation():

    @staticmethod
    def create_new(members, title=""):
        print("CREATE NEW members ", members)
        chats_same_members = Chat.objects(members=members, title=title)

        print("chats same members ", chats_same_members)

        if not chats_same_members:
            print("members ", members)
            chat = Chat(title=title, members=members).save()
        else:
            raise Exception("Chat with same members already exists")
        return chat



