from mongoengine import *
import mongoengine_goodjson as gj
from datetime import datetime
from flask_login import UserMixin


class User(gj.Document, UserMixin):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, exclude_to_json=True)
    token = StringField()

    last_sign_in = DateTimeField()
    date_created = DateTimeField(default=datetime.utcnow, exclude_to_json=True)

    def __str__(self):
        return "id: {}, name: {}, email: {}".format(self.id, self.name, self.email)
