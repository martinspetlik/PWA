from mongoengine import *


class RevokedTokens(Document):
    jti = StringField(required=True)
