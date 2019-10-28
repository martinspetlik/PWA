from mongoengine import *
from datetime import datetime


class User(Document):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    last_sign_in = DateTimeField()
    date_created = DateTimeField(default=datetime.utcnow)

    # first_name = StringField()
    # last_name = StringField()
    # age = IntField()
    # signed_in = BooleanField(default=False)

    def __str__(self):
        return "id: {}, name: {}, email: {}".format(self.id, self.name, self.email)

