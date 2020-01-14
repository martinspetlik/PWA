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


import datetime
#from app import app
from flask_login import login_required, current_user, login_user, logout_user

from flask_restful import Resource
from flask import url_for, session, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from mongoengine.errors import ValidationError
from flask_mail import Mail
from flask_mail import Message as MailMessage
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from server.models.user import User
from server.models.chat import Chat as Chat_db
from server.models.chat import ChatCreation
from server.models.message import Message


app = Flask(__name__, static_folder="./client/dist", template_folder="./client")
app.secret_key = 'super secret key'
socketio = SocketIO(app, cors_allowed_origins="*")#, manage_session=False)

login_manager = LoginManager()

s = URLSafeTimedSerializer('73637979')

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'pwachatapp@gmail.com',
    "MAIL_PASSWORD": 'pwachatapp2019'
}
app.config.update(mail_settings)

mail = Mail(app)

database_url = os.environ.get("DATABASE_URL")
print("database url ", database_url)

if database_url is not None:
    host = database_url
else:
    host = 'mongodb://127.0.0.1:27017'

print("database host ", host)

connect("chat", host=host)

print("connected")
#api = Api(app)

app.config['JWT_SECRET_KEY'] = 'jwt-secret-string'
jwt = JWTManager(app)

app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return True if RevokedTokens.objects(jti=jti) else False


# api.add_resource(UserRegistration, '/registration')
# api.add_resource(UserLogin, '/')
# #api.add_resource(resources.UserProfile, '/profile')
# api.add_resource(PasswordResetEmail, '/reset')
# api.add_resource(PasswordReset, '/reset/<token>')
#
# api.add_resource(Chats, '/chats')
# api.add_resource(Chat, '/chat/<id>')
# api.add_resource(ChatAdd, '/chats/add')

# api.add_resource(UserLogoutAccess, '/logout')

app.config.from_object('config.config.ProductionConfig')
app.config['SECRET_KEY'] = '9OLWxND4o83j4K4iuopO'

login_manager.init_app(app)
#socketio.run(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registration', methods=['POST'])
def post_registration():
    email = request.get_json().get('email')
    name = request.get_json().get('name')
    password = request.get_json().get('password')

    print("requeat json ", request.get_json())

    if password == "":
        return jsonify({"success": False, "message": 'Empty password'})

    user = User.objects(email=email).first()  # if this returns a user, then the email already exists in database
    user_name_exist = User.objects(name=name).first()

    print("user ", user)

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return jsonify({"success": False, "message": 'User with this email address already exists', "email": email})

    if user_name_exist:
        return jsonify({"success": False, "message": 'User with this name already exists', "email": email})

    try:
        # create new user with the form data. Hash the password so plaintext version isn't saved.
        user = User(email=email, name=name, password=generate_password_hash(password, method='sha256')).save()

    except ValidationError as err:
        return jsonify({"success": False, "message": err.message})

    return jsonify({"success": True, "message": 'email ' + user.email + ' successfully registered'})


@app.route('/', methods=['POST'])
def post_login():
    email = request.get_json()['email']
    password = request.get_json()['password']
    user = User.objects(email=email).first()

    expires = datetime.timedelta(days=1)

    print("user ", user)

    if user:
        login_user(user)

        if check_password_hash(user.password, password):
            #access_token = create_access_token(identity={'name': user.name, 'email': user.email}, expires_delta=expires)
            #user.update(token=access_token)

            access_token = "sdasdf"

            print("access token ", access_token)

            return jsonify({
                'success': True,
                'message': 'Logged in as {}'.format(user.name),
                'access_token': access_token,
                'user_name': user.name,
            }), 200
        else:
            return jsonify({"success": False, 'message': 'Wrong credentials'})
    else:
        return jsonify({"success": False, "message": "Invalid user email"})


def _get_all_chats(current_user):
    user = User.objects(name=current_user["name"]).first()
    chats = Chat_db.objects(members__contains=user).order_by('last_message_date')

    response = []
    for chat in chats:
        chat.members.remove(user)
        chat_members = ""

        for member in chat.members:
            chat_members += member.name
            chat_members + " "
        response.append({"members": chat_members, "title": chat.title, "id": str(chat.id)})

    return response

@app.route('/chats', methods=['GET'])
@login_required
def get_chats():
    chats_output = _get_all_chats(current_user)
    print("chats output ", chats_output)
    return jsonify(chats_output)


@app.route('/reset', methods=['GET'])
def get_reset():
    print("request ", request)
    print("request token ", request.args["token"])


@app.route('/reset', methods=['POST'])
def post_reset():
    """
    Handle post request, send email, save token to database
    :return:
    """
    email = request.get_json()['email']
    cur_user = User.objects(email=email).first()

    if not cur_user:
        return jsonify({"success": False, "message": "No user has this email: {}".format(email)}), 200

    token = s.dumps(email, salt='email-password-reset')
    msg = MailMessage('Confirm Email', sender=mail_settings["MAIL_USERNAME"], recipients=[email])
    link = "https://pwachat2.herokuapp.com/?token={}".format(token)
    msg.body = 'Your link is {}'.format(link)
    mail.send(msg)

    return jsonify({"success": True, "message": "Email was sent to: {}".format(email)}), 200


@app.route('/reset/<token>', methods=['POST'])
def post_reset_token(token):
    """
    Render form
    :return:
    """
    email = request.get_json().get('email')
    password = request.get_json().get('password')

    try:
        token_email = s.loads(token, salt='email-password-reset', max_age=3600)
    except SignatureExpired:
        return jsonify({"success": False, "message": "The token is expired!"})

    if email != token_email:
        return jsonify({"success": False, "message": "Bad email"}), 200

    user = User.objects(email=email).first()
    user.update(password=generate_password_hash(password, method='sha256'))

    return jsonify({"success": True, "message": "Password was changed"}), 200


@app.route('/reset/<token>', methods=['GET'])
def get_reset_token(token):
    """
    Render form
    :return:
    """
    try:
        email = s.loads(token, salt='email-password-reset', max_age=3600)
    except SignatureExpired:
        return jsonify({"success": False, "message": "The token is expired!"})
    except Exception:
        return jsonify({"success": False, "message": "Invalid token"})

    return jsonify({"success": True, "message": "Everything OK", "email": email}), 200


# class UserProfile(Resource):
#     @login_required
#     def get(self):
#         current_user = get_jwt_identity()
#         return {"name": current_user['name'], "email": current_user['email']}


@app.route('/chat/<id>', methods=['DELETE'])
@login_required
def delete_chat(id):
    chat = Chat_db.objects(id=id).first()

    if not chat:
        return jsonify({"success": False, "message": "Chat not exist"}), 400
    else:

        Chat_db.objects(id=id).delete()
        Message.objects(chat=id).delete()

    chat = Chat_db.objects(id=id).first()

    if not chat:
        return jsonify({"success": True, "message": "Chat was deleted"}), 200

    return jsonify({"success": False, "message": "Delete failed, try it again"}), 200


@app.route('/chat/<id>', methods=['GET'])
@login_required
def get_chat_id(id):
    messages = Message.objects(chat=id)

    message_dict = {}
    for message in messages:
        user = User.objects(name=current_user["name"]).first()
        if message.author.id == user.id:
            status = "sent"
        else:
            status = "replies"

        message_dict[str(message.date_created)] = {"text": message.text, "status": status, "author": message.author.name}

    return jsonify(message_dict)

@app.route('/chat/<id>', methods=['POST'])
@login_required
def post_chat_id(id):
    author = request.get_json().get('author')
    text = request.get_json().get('text')

    chat = Chat_db.objects(id=id).first()
    user = User.objects(name=author).first()

    if user not in chat.members:
        return jsonify({"success": False, "message": "This user is not part of current chat"}), 400

    message = Message(author=user, chat=chat, text=text).save()

    if message is not None:
        return jsonify({"success": True, "message": "Message was sent"}), 200


@app.route('/chats/add', methods=['POST'])
@login_required
def post_chats_add():
    title = request.get_json()['title']
    members = request.get_json()['members']

    cur_user = User.objects(id=current_user["id"]).first()

    chat_members = []
    for member in members:
        user = User.objects(name=member["label"], email=member["value"]).first()

        if cur_user.id == user.id:
            return jsonify({"success": False, "message": "It is not allowed to chat with yourself".format(member)}), 400

        if user is None:
            return jsonify({"success": False, "message": "User not exists {}".format(member)}), 200

        chat_members.append(user)

    chat_members.append(cur_user)


    try:
        new_chat = ChatCreation.create_new(title=title, members=chat_members).save()
    except:
        return jsonify({"success": False, "message": "Chat with same users already exist"}), 400

    return jsonify({"success": True, "message": "New chat created, title: {}, members: {}".format(new_chat.title, new_chat.members),
            "chat": {"members": ",".join([m.name for m in chat_members]),
                     "title": new_chat.title, "id": str(new_chat.id)}}), 200


@app.route('/chats/add', methods=['GET'])
@login_required
def get_chats_add():
    """
    Load chat addition form
    :return:
    """
    all_users = User.objects(email__nin=[current_user["email"]])

    users = []
    for index, user in enumerate(all_users):
        if user.id == current_user["id"]:
            continue
        users.append({"label": user.name, "value": user.email})

    return jsonify(users)

@app.route('/logout', methods=['POST'])
@login_required
def post_logout():
    user = User.objects(email=current_user["email"]).first()
    user.update(token="")
    logout_user()
    session.clear()

    return jsonify({"message": "User was logged out"}), 200


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


# def create_app():
#
#     return app


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


if __name__ == "__main__":

    #app = create_app()
    #renew_database()
    login_manager.init_app(app)
    #create_conversations()

    socketio.run(app)#, debug=True)
