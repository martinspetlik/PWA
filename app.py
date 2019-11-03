import os
from mongoengine import *
from flask import Flask, jsonify, request, json
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended import create_access_token

#from .auth import auth as auth_blueprint

from server.models.user import User
from server.models.message import Message
from server.models.conversation import Conversation

from server.models.revoked_tokens import RevokedTokens

from flask import Flask
from flask_login import LoginManager


from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

app = Flask(__name__)


def create_app():
    app = Flask(__name__)
    connect("chat")

    api = Api(app)

    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    jwt = JWTManager(app)

    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return True if RevokedTokens.objects(jti=jti) else False

    import resources

    api.add_resource(resources.UserRegistration, '/registration')
    api.add_resource(resources.UserLogin, '/')
    api.add_resource(resources.UserProfile, '/profile')
    api.add_resource(resources.UserLogoutAccess, '/logout')
    api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
    api.add_resource(resources.TokenRefresh, '/token/refresh')


    app.config.from_object('config.config.ProductionConfig')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

    return app


if __name__ == "__main__":
    app = create_app()
    print("app.config['TESTING']", app.config['TESTING'])
    app.run()

