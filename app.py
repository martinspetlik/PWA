import os
from mongoengine import connect
from flask import Flask, render_template
from flask_restful import Api
from flask_jwt_extended import JWTManager, get_jwt_identity
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_login import LoginManager, current_user

from server.models.user import User
from server.models.message import Message
from server.models.chat import Chat
from server.models.chat import ChatCreation
from server.models.revoked_tokens import RevokedTokens

app = Flask(__name__, static_folder="./client/dist", template_folder="./client")
app.secret_key = 'super secret key'
# app.config['SESSION_TYPE'] = 'filesystem'
# #Session(app)
socketio = SocketIO(app, cors_allowed_origins="*")#, manage_session=False)


login_manager = LoginManager()


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def connect_handler():

    if current_user.is_authenticated:
        emit('my response',
             {'message': '{0} has joined'.format(current_user.name)},
             broadcast=True)
    else:
        return False  # not allowed here


@socketio.on("all_users")
def load_users():
    """
    Load chat addition form
    :return:
    """
    if current_user.is_authenticated:
        all_users = User.objects(email__nin=[current_user["email"]])

        users = []
        for user in all_users:
            if user.id == current_user["id"]:
                continue

            users.append([user.name, user.email])

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
        chat = Chat.objects(id=id).first()
        chat_members_ids = [member.id for member in chat.members]
        if current_user["id"] not in chat_members_ids:
            emit('all_messages', [False], room=id)
        else:

            messages = Message.objects(chat=id)
            messages = list(messages)[-50:]
            messages.sort(key=lambda x: x.id, reverse=False)

            all_messages = []
            status = ""
            for message in messages:
                user = User.objects(name=current_user["name"]).first()
                # if message.author.id == user.id:
                #     status = "sent"
                # else:
                #     status = "replies"

                all_messages.append([message.author.name, message.text, str(message.date_created), status])

            emit('all_messages', all_messages, room=id)

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
        #print("LOAD messages not authenticated")
        emit('all_messages', [False], room=id)

    # print("message_dict ", message_dict)
    # emit('all_messages', message_dict, broadcast=True, room=id)
    #
    # # user = User.objects(name=msg['author']).first()
    # chat = Chat.objects(id=room).first()
    # Message(author=user, chat=chat, text=msg['text']).save()


@socketio.on("message")
def handle_message(msg, room):
    user = User.objects(name=msg['author']).first()
    chat = Chat.objects(id=room).first()
    Message(author=user, chat=chat, text=msg['text']).save()

    status = ""

    if current_user.is_authenticated:
        # if msg["author"] == current_user["name"]:
        #     status = "sent"
        # else:
        #     status = "replies"

        message = [msg["author"], msg["text"], str(1), status]

        send(message, room=room)
    else:
        send(False, room=room)


@socketio.on('join')
def on_join(data):
    if current_user.is_authenticated:
        username = data['username']
        room = data['room']
        join_room(room)
        send(username + ' has entered the room.', room=room)


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
    database_url = os.environ.get("DATABASE_URL")

    if database_url is not None:
        host = database_url
    else:
        host = 'mongodb://127.0.0.1:27017'

    connect("chat", host=host)
    api = Api(app)

    app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
    jwt = JWTManager(app)

    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']

    @jwt.token_in_blacklist_loader
    def check_if_token_in_blacklist(decrypted_token):
        jti = decrypted_token['jti']
        return True if RevokedTokens.objects(jti=jti) else False

    import server.resources as resources

    api.add_resource(resources.UserRegistration, '/registration')
    api.add_resource(resources.UserLogin, '/')
    #api.add_resource(resources.UserProfile, '/profile')
    api.add_resource(resources.PasswordResetEmail, '/reset')
    api.add_resource(resources.PasswordReset, '/reset/<token>')

    api.add_resource(resources.Chats, '/chats')
    api.add_resource(resources.Chat, '/chat/<id>')
    api.add_resource(resources.ChatAdd, '/chats/add')

    api.add_resource(resources.UserLogoutAccess, '/logout')
    app.config.from_object('config.config.ProductionConfig')
    app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'
    return app


def create_conversations():
    user1 = User.objects(name="test").first()
    user2 = User.objects(name="test2").first()

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
    user = User.objects(id=user_id).first()
    return user


@login_manager.request_loader
def load_user_from_request(request):
    token = request.headers.get('Authorization')
    if token:
        token = token.replace('Bearer ', '', 1)
        try:
            token = token
        except TypeError:
            pass
        user = User.objects(token=token).first()
        if user:
            return user

    # finally, method did not login the user
    return None


def renew_database():
    from werkzeug.security import generate_password_hash, check_password_hash
    Chat.objects.delete()
    Message.objects.delete()
    User.objects.delete()

    user1 = User(name="user1", email='test@test.cz', password=generate_password_hash("test", method='sha256')).save()
    user2 = User(name="user2", email='test2@test.cz', password=generate_password_hash("test", method='sha256')).save()
    user3 = User(name="user3", email='test3@test.cz', password=generate_password_hash("test", method='sha256')).save()

    user4 = User(name="user4", email='martin.spetlik@tul.cz', password=generate_password_hash("test", method='sha256')).save()

    chat1 = ChatCreation.create_new(members=[user1, user2])
    chat2 = ChatCreation.create_new(members=[user1, user3])

    Message(text="Zprava user1", author=user1, chat=chat1).save()
    Message(text="Zprava user2", author=user2, chat=chat1).save()
    Message(text="Zprava user1", author=user1, chat=chat1).save()

    Message(text="Zprava user1 chat 2", author=user1, chat=chat2).save()
    Message(text="Zprava user2 chat2", author=user3, chat=chat2).save()


# if __name__ == "__main__":
#
#     app = create_app()
#     renew_database()
#     login_manager.init_app(app)
#     #create_conversations()
#
#     socketio.run(app)#, debug=True)






