
from mongoengine import connect
from server.models.user import User
from server.models.message import Message
from server.models.chat import Chat
from server.models.chat import ChatCreation

from server.models.revoked_tokens import RevokedTokens

from flask_restful import Resource

from flask import Flask, request
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO, send, disconnect, emit, join_room, leave_room
from flask_session import Session

from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from flask_cors import CORS
from flask_login import LoginManager, login_required, current_user, login_user, logout_user


app = Flask(__name__,  template_folder='client/public')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
#Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")#, manage_session=False)
#CORS(app)

login_manager = LoginManager()

@socketio.on('connect')
def connect_handler():
    print("CONNECT EVENT")
    print("current user ", current_user)
    print("request session id ", request.cookies)

    cur_user = get_jwt_identity()

    print("cur user ", cur_user)
    if current_user.is_authenticated:
        print("CONNECT IS AUTHENTICATED")
        emit('my response',
             {'message': '{0} has joined'.format(current_user.name)},
             broadcast=True)
    else:
        disconnect()
        print("CONNECT IS NOT AUTHENTICATED")
        return False  # not allowed here


@socketio.on("all_users")
def load_users():
    """
    Load chat addition form
    :return:
    """
    print("LOAD USERS")
    if current_user.is_authenticated:
        all_users = User.objects(email__nin=[current_user["email"]])

        users = []
        for user in all_users:
            if user.id == current_user["id"]:
                continue

            users.append([user.name, user.email])

        print("users ", users)
        emit('all_users', users)
    else:
        emit('all_users', False)

@socketio.on("load_messages")
def load_messages(id):
    """
    Get messages
    :param id: chat id
    :return: last 50 messages
    """
    if current_user.is_authenticated:
        print("chat ID ", id)
        messages = Message.objects(chat=id)
        print("messages from DB ", messages)
        messages = list(messages)[:50]

        messages.sort(key=lambda x: x.id, reverse=False)

        print("messages ", messages)

        all_messages = []
        for message in messages:
            user = User.objects(name=current_user["name"]).first()
            if message.author.id == user.id:
                status = "sent"
            else:
                status = "replies"

            all_messages.append([message.author.name, message.text, str(message.date_created), status])

        emit('all_messages', all_messages, broadcast=True, room=id)

        # message_dict = {}
        # for message in messages:
        #     user = User.objects(name=current_user["name"]).first()
        #     if message.author.id == user.id:
        #         status = "sent"
        #     else:
        #         status = "replies"
        #
        #     message_dict[str(message.id)] = {"text": message.text, "status": status,
        #                                                "author": message.author.name}
        #     print("message ", message)
    else:
        print("LOAD messages not authenticated")
        emit('all_messages', [False], broadcast=True, room=id)

    # print("message_dict ", message_dict)
    # emit('all_messages', message_dict, broadcast=True, room=id)
    #
    # # user = User.objects(name=msg['author']).first()
    # chat = Chat.objects(id=room).first()
    # Message(author=user, chat=chat, text=msg['text']).save()



@socketio.on("message")
def handle_message(msg, room):
    print("message ", msg)
    print("room ", room)

    user = User.objects(name=msg['author']).first()
    chat = Chat.objects(id=room).first()
    Message(author=user, chat=chat, text=msg['text']).save()

    if current_user.is_authenticated:
        if msg["author"] == current_user["name"]:
            status = "sent"
        else:
            status = "replies"

        message = [msg["author"], msg["text"], str(1), status]

        # print("message ", message)
        # print("msg ", msg)

        send(message, broadcast=True, room=room)
    else:
        send(False, broadcast=True, room=room)


@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        print("JOIN ", data)
        username = data['username']
        room = data['room']
        join_room(room)
        send(username + ' has entered the room.', room=room)
    else:
        print("JOIN user auth ", current_user.is_authenticated)


@socketio.on('leave')
def on_leave(data):
    if current_user.is_authenticated:
        username = data['username']
        room = data['room']
        leave_room(room)
        send(username + ' has left the room.', room=room)
    else:
        return False


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
    #api.add_resource(resources.Login, '/login')
    #api.add_resource(resources.Authorized, '/authorized')
    api.add_resource(resources.UserProfile, '/profile')
    api.add_resource(resources.PasswordResetEmail, '/reset')
    api.add_resource(resources.PasswordReset, '/reset/<token>')

    api.add_resource(resources.Chats, '/chats')
    api.add_resource(resources.Chat, '/chat/<id>')
    api.add_resource(resources.ChatAdd, '/chats/add')

    api.add_resource(resources.UserLogoutAccess, '/logout')
    #api.add_resource(resources.UserLogoutRefresh, '/logout/refresh')
    #api.add_resource(resources.TokenRefresh, '/token/refresh')


    app.config.from_object('config.config.ProductionConfig')

    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

    return app


def create_conversations():
    user1 = User.objects(name="test").first()
    user2 = User.objects(name="test2").first()

    print("user 1 ", user1)
    print("user 2 ", user2)

    try:
        ChatCreation.create_new(members=[user1, user2])
        conv1 = Chat.objects(members=[user1, user2]).first()

        Message(text="Testovací zpráva autora test", author=user1, chat=conv1).save()

        Message(text="Testovací zpráva autora test3", author=user2, chat=conv1).save()

        Message(text="1. Testovací zpráva autora test", author=user1, chat=conv1).save()

        m1 = Message(text="3. Testovací zpráva autora test", author=user1, chat=conv1).save()
        conv1.update(last_message_date=m1.date_created)

    except Exception as e:
        print(str(e))


@login_manager.user_loader
def load_user(user_id):
    print("USER LOADER id ", user_id)
    user = User.objects(id=user_id).first()
    print("user ", user)
    return user


def renew_database():
    from werkzeug.security import generate_password_hash, check_password_hash
    Chat.objects.delete()
    Message.objects.delete()
    User.objects.delete()

    user1 = User(name="user1", email='test@test.cz', password=generate_password_hash("test", method='sha256')).save()
    user2 = User(name="user2", email='test2@test.cz', password=generate_password_hash("test", method='sha256')).save()
    user3 = User(name="user3", email='test3@test.cz', password=generate_password_hash("test", method='sha256')).save()

    print("user1 ", user1)

    chat1 = ChatCreation.create_new(members=[user1, user2])
    chat2 = ChatCreation.create_new(members=[user1, user3])

    print("chat1 ", chat1)

    Message(text="Zprava user1", author=user1, chat=chat1).save()
    Message(text="Zprava user2", author=user2, chat=chat1).save()
    Message(text="Zprava user1", author=user1, chat=chat1).save()

    Message(text="Zprava user1 chat 2", author=user1, chat=chat2).save()
    Message(text="Zprava user2 chat2", author=user2, chat=chat2).save()


if __name__ == "__main__":

    app = create_app()
    #renew_database()
    login_manager.init_app(app)
    #create_conversations()
    print("app.config['TESTING']", app.config['TESTING'])
    print("socket io ", socketio)

    socketio.run(app, debug=True)






