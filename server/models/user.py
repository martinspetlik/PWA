from mongoengine import *
import mongoengine_goodjson as gj
from datetime import datetime
from flask_login import UserMixin


class User(gj.Document, UserMixin):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True, exclude_to_json=True)
    authenticated = BooleanField(required=True, default=False)

    last_sign_in = DateTimeField()
    date_created = DateTimeField(default=datetime.utcnow, exclude_to_json=True)

    # @staticmethod
    # def is_authenticated():
    #     return True
    #
    # @staticmethod
    # def is_active():
    #     return True
    #
    # @staticmethod
    # def is_anonymous():
    #     return False
    #
    # def get_id(self):
    #     return self.email

    # def is_authenticated(self):
    #     return self.authenticated
    # #
    # # @is_authenticated.setter
    # # def is_authenticated(self, value):
    # #     self.authenticated = value
    #
    # def is_active(self):
    #     return True
    #
    # def is_anonymous(self):
    #     return False
    #
    # def get_id(self):
    #     return self.id



    # first_name = StringField()
    # last_name = StringField()
    # age = IntField()
    # signed_in = BooleanField(default=False)

    def __str__(self):
        return "id: {}, name: {}, email: {}".format(self.id, self.name, self.email)


