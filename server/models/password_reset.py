from mongoengine import *
import mongoengine_goodjson as gj
from datetime import datetime
from server.models.user import User


class PasswordReset(gj.Document):
    user = gj.FollowReferenceField(User, required=True)
    token = StringField(required=True)
    time = DateTimeField(default=datetime.utcnow)
