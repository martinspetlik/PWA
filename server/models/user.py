from mongoengine import *
from datetime import datetime

from flask_login import UserMixin, login_manager


class User(UserMixin, Document):
    name = StringField(required=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)

    last_sign_in = DateTimeField()
    date_created = DateTimeField(default=datetime.utcnow)

    # def is_authenticated(self):
    #     return True
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
#
# @login_manager.user_loader
# def load_user(user_id):
#     user = User.objects(name=user_id)[0]
#     return user