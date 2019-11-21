
from mongoengine import *
from server.models.user import User
from server.models.message import Message
from server.models.chat import Chat
from server.models.chat import Chat_db

from server.models.revoked_tokens import RevokedTokens

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, send

app = Flask(__name__)
socketio = SocketIO(app)


def create_app():
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
    api.add_resource(resources.Chats, '/chats')
    api.add_resource(resources.Chat, '/chat/<id>')
    api.add_resource(resources.UserLogoutAccess, '/logout')
    api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
    api.add_resource(resources.TokenRefresh, '/token/refresh')


    app.config.from_object('config.config.ProductionConfig')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

    return app


def create_conversations():
    user1 = User.objects(name="test").first()
    user2 = User.objects(name="test2").first()

    print("user 1 ", user1)
    print("user 2 ", user2)

    try:
        Chat_db.create_new(members=[user1, user2])
        conv1 = Chat.objects(members=[user1, user2]).first()

        Message(text="Testovací zpráva autora test", author=user1, chat=conv1).save()

        Message(text="Testovací zpráva autora test3", author=user2, chat=conv1).save()

        Message(text="1. Testovací zpráva autora test", author=user1, chat=conv1).save()

        m1 = Message(text="3. Testovací zpráva autora test", author=user1, chat=conv1).save()
        conv1.update(last_message_date=m1.date_created)

    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    app = create_app()
    #create_conversations()
    print("app.config['TESTING']", app.config['TESTING'])

    socketio = SocketIO(app)
    socketio.run(app)

    print("socket io ", socketio)





