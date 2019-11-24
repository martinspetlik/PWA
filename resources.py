from app import socketio

from app import app

from flask_socketio import send, emit, join_room, leave_room

from app import login_manager

from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from flask_restful import Resource
from flask import Flask, redirect, url_for, session, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from mongoengine.errors import ValidationError
from server.models.revoked_tokens import RevokedTokens

from server.models.user import User
from server.models.chat import Chat as Chat_db
from server.models.message import Message

# from flask_oauthlib.client import OAuth
#
# app.config['GOOGLE_ID'] = "9200143057-icc83i692fcceah2u1jljtd1cuku5ujn.apps.googleusercontent.com"
# app.config['GOOGLE_SECRET'] = "NhilszuwT3UcbqmLQL1dYiT5 "
# app.debug = True
# app.secret_key = 'development'
# oauth = OAuth(app)


class UserRegistration(Resource):

    def post(self):
        email = request.get_json().get('email')
        name = request.get_json().get('name')
        password = request.get_json().get('password')

        print("request.get_json() ", request.get_json())

        print("email ", email)
        print("name ", name)
        print("password ", password)

        user = User.objects(email=email).first()  # if this returns a user, then the email already exists in database
        user_name_exist = User.objects(name=name).first()

        if user:  # if a user is found, we want to redirect back to signup page so user can try again
            return jsonify({"success": False, "message": 'User with this email address already exists', "email": False})

        if user_name_exist:
            return jsonify({"success": False, "message": 'User with this name already exists', "email": True})

        try:
            # create new user with the form data. Hash the password so plaintext version isn't saved.
            user = User(email=email, name=name, password=generate_password_hash(password, method='sha256')).save()

        except ValidationError as err:
            return jsonify({"success": False, "message": err.message})

        print("user ", user)

        return jsonify({"success": True, "message": 'email ' + user.email + ' successfully registered'})

# @login_manager.request_loader
# def load_user_from_request(request):
#
#     # first, try to login using the api_key url arg
#     api_key = request.args.get('api_key')
#     if api_key:
#         user = User.query.filter_by(api_key=api_key).first()
#         if user:
#             return user
#
#     # next, try to login using Basic Auth
#     api_key = request.headers.get('Authorization')
#     if api_key:
#         api_key = api_key.replace('Basic ', '', 1)
#         try:
#             api_key = base64.b64decode(api_key)
#         except TypeError:
#             pass
#         user = User.query.filter_by(api_key=api_key).first()
#         if user:
#             return user
#
#     # finally, return None if both methods did not login the user
#     return None


class UserLogin(Resource):
    def get(self):
        print("landing page")

    def post(self):
        print("LOGIN")

        # users = User.objects()
        # print("users ", users)

        print("request get json ", request.get_json())

        email = request.get_json()['email']
        password = request.get_json()['password']

        print("email ", email)
        print("password ", password)

        # remember = True if request.form.get('remember') else False

        user = User.objects(email=email).first()

        print("Login user ", user)
        print("login user type ", type(user))

        #@TODO: remove ASAP
        import datetime
        expires = datetime.timedelta(days=365)

        if user:
            login_user(user)

            if check_password_hash(user.password, password):
                access_token = create_access_token(identity={'name': user.name, 'email': user.email}, expires_delta=expires)
                refresh_token = create_refresh_token(identity={'name': user.name, 'email': user.email}, expires_delta=expires)
                return {
                    'success': True,
                    'message': 'Logged in as {}'.format(user.name),
                    'access_token': access_token,
                    'user_name': user.name,
                    'refresh_token': refresh_token
                }
            else:
                return {"success": False, 'message': 'Wrong credentials'}
        else:
            return {"success": False, "message": "Invalid user email"}

        # access token has 15 minutes lifetime
        # print("access token ", access_token)

        return result


class UserProfile(Resource):
    @login_required
    def get(self):
        print("PROFILE")
        current_user = get_jwt_identity()

        print("current user ", current_user)

        return {"name": current_user['name'], "email": current_user['email']}


@socketio.on("message_test")
def message_test():
    print("message TEST")

    with open("/home/martin/Documents/PWA/test.txt", "w")as writer:
        writer.write("message TEST")

    emit("Message TEST", broadcast=True)


class Chat(Resource):
    @login_required
    def get(self, id):
        messages = Message.objects(chat=id)

        message_dict = {}
        for message in messages:
            user = User.objects(name=current_user["name"]).first()
            if message.author.id == user.id:
                status = "sent"
            else:
                status = "replies"

            message_dict[str(message.date_created)] = {"text": message.text, "status": status, "author": message.author.name}
            print("message ", message)

        print("message_dict ", message_dict)
        return message_dict

    # @socketio.on('message')
    # def on_chat_sent(self, data):
    #     room = data['room']
    #     emit('message_sent', data, room=room)

    @socketio.on('join')
    def on_join(self, data):
        username = data['username']
        room = data['room']
        join_room(room)
        emit(username + ' has entered the room.', room=room)

    @socketio.on('leave')
    def on_leave(self, data):
        username = data['username']
        room = data['room']
        leave_room(room)
        emit(username + ' has left the room.', room=room)

    @socketio.on('message')
    def handle_message(self, msg, room=None):
        print("message ", msg)
        print("message dist ", msg.__dict__)

        emit(msg, broadcast=True)#, room=room)


class Chats(Resource):

    def _get_all_chats(self, current_user):
        print("get all chats")

        user = User.objects(name=current_user["name"]).first()
        chats = Chat_db.objects(members__contains=user).order_by('last_message_date')

        response = {}
        for chat in chats:
            chat.members.remove(user)
            chat_members = ""

            for member in chat.members:
                chat_members += member.name
                chat_members + " "
            response[str(chat.id)] = {"members": chat_members}

        print("response ", response)

        return response

    @login_required
    def get(self):
        print("CHATS GET")
        #current_user = get_jwt_identity()
        chats_output = self._get_all_chats(current_user)

        return chats_output

        #return chats.to_json()

        chats_output = {}
        chats_output['current_user'] = user.name
        chats_output['chats'] = []

        for chat in chats:
            print("chat members ", chat.members)
            chat.members.remove(user)
            print("chat members removed current user", chat.members)
            # messages = Message.objects(chat=chat)
            # print("messages ", messages)
            # print("messages to json ", messages.to_json())

            # if len(messages) > 0:
            #     print("messages[0].author ", messages[0].author)
            #     print("messages[0].to json ", messages[0].to_json())

            chats_output['chats'].append({"members": [member.to_json() for member in chat.members],
                                          "messages": messages.to_json()})

        for chat in chats_output['chats']:
            print("chat ", chat)

        return chats_output
        print("chats_output ", chats_output)
        return "OK"
        #return chats


class UserLogoutAccess(Resource):
    @login_required
    def post(self):
        print("user logout")

        logout_user()

        # try:
        #     revoked_token = RevokedTokens(jti=jti)
        #     revoked_token.save()
        #     return {'message': 'Access token has been revoked'}
        # except:
        #     return {'message': 'Something went wrong'}, 500


# class UserLogoutRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         jti = get_raw_jwt()['jti']
#         try:
#             revoked_token = RevokedTokens(jti=jti)
#             revoked_token.save()
#             return {'message': 'Refresh token has been revoked'}
#         except:
#             return {'message': 'Something went wrong'}, 500


# class TokenRefresh(Resource):
#     @jwt_refresh_token_required
#     def post(self):
#         current_user = get_jwt_identity()
#         access_token = create_access_token(identity=current_user)
#         return {'access_token': access_token}

