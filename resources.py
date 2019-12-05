from app import socketio

from app import app

import uuid

from flask_socketio import send, emit, join_room, leave_room
from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from flask_restful import Resource
from flask import Flask, redirect, url_for, session, request, jsonify, render_template, \
    send_from_directory, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from mongoengine.errors import ValidationError
from server.models.revoked_tokens import RevokedTokens

from flask_mail import Mail
from flask_mail import Message as MailMessage

from itsdangerous import URLSafeTimedSerializer, SignatureExpired

from server.models.user import User
from server.models.chat import Chat as Chat_db
from server.models.chat import ChatCreation
from server.models.message import Message
from server.models.password_reset import PasswordReset as PasswordReset_db

s = URLSafeTimedSerializer('Thisisasecret!')

mail = Mail(app)

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
        email = request.get_json()['email']
        password = request.get_json()['password']
        user = User.objects(email=email).first()

        print("Login user ", user)

        #@TODO: remove ASAP
        import datetime
        expires = datetime.timedelta(days=365)

        if user:
            print("if user")
            login_user(user)

            print("current user ", current_user)
            print("login current user is authenticated ", current_user.is_authenticated)

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


class Chats(Resource):
    def _get_all_chats(self, current_user):
        print("get all chats")
        print("current user name ", current_user["name"])

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

        print("response ", response)

        return response

    @login_required
    def get(self):
        print("CHATS GET")

        print("current user ", current_user)

        print("get chats current user is auth", current_user.is_authenticated)
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


class PasswordResetEmail(Resource):

    def get(self):
        print("request ", request)
        print("request token ", request.args["token"])

    def post(self):
        """
        Handle post request, send email, save token to database
        :return:
        """
        print("PASSWORD RESET EMAIL")
        email = request.get_json()['email']
        print("email ", email)
        cur_user = User.objects(email=email).first()

        print("reset email user ", cur_user)

        if not cur_user:
            return {"success": False, "message": "No user has this email: {}".format(email)}

        #PasswordReset_db(user=cur_user, token=token).save()
        token = s.dumps(email, salt='email-password-reset')
        msg = MailMessage('Confirm Email', sender='spetlik.martin@seznam.cz', recipients=[email])
        link = url_for('passwordreset', token=token, _external=True)
        link = "http://localhost:3000/reset/{}".format(token)
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)

        return {"success": True, "message": "Email was sent to: {}".format(email)}


class PasswordReset(Resource):

    def post(self, token):
        """
        Render form
        :return:
        """
        email = request.get_json().get('email')
        password = request.get_json().get('password')

        try:
            token_email = s.loads(token, salt='email-password-reset', max_age=3600)
        except SignatureExpired:
            return {"success": False, "message": "The token is expired!"}

        if email != token_email:
            return {"success": False, "message": "Bad email"}

        user = User.objects(email=email).first()
        user.update(password=generate_password_hash(password, method='sha256'))

        return {"success": True, "message": "Password was changed"}

    def get(self, token):
        """
        Render form
        :return:
        """
        try:
            email = s.loads(token, salt='email-password-reset', max_age=3600)
        except SignatureExpired:
            return {"success": False, "message": "The token is expired!"}

        return {"success": True, "message": "Everything OK", "email": email}


class UserProfile(Resource):
    @login_required
    def get(self):
        print("PROFILE")
        current_user = get_jwt_identity()

        print("current user ", current_user)

        return {"name": current_user['name'], "email": current_user['email']}


class Chat(Resource):
    @login_required
    def delete(self, id):
        print("chat id ", id)
        chat = Chat_db.objects(id=id).first()
        print("chat ", chat)

        if not chat:
            return {"success": False, "message": "Chat not exist"}
        else:

            Chat_db.objects(id=id).delete()
            Message.objects(chat=id).delete()

        chat = Chat_db.objects(id=id).first()

        if not chat:
            return {"success": True, "message": "Chat was deleted"}

        return {"success": False, "message": "Delete failed, try it again"}

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

    def post(self):
        email = request.get_json().get('email')
        name = request.get_json().get('name')
        password = request.get_json().get('password')
        print("request.get_json() ", request.get_json())


    # @socketio.on('join')
    # def on_join(self, data):
    #     username = data['username']
    #     room = data['room']
    #     join_room(room)
    #     emit(username + ' has entered the room.', room=room)
    #
    # @socketio.on('leave')
    # def on_leave(self, data):
    #     username = data['username']
    #     room = data['room']
    #     leave_room(room)
    #     emit(username + ' has left the room.', room=room)
    #
    # @socketio.on('message')
    # def handle_message(self, msg, room=None):
    #     print("message ", msg)
    #     print("message dist ", msg.__dict__)
    #
    #     emit(msg, broadcast=True)#, room=room)


class ChatAdd(Resource):

    @login_required
    def post(self):
        title = request.get_json()['title']
        members = request.get_json()['members']

        cur_user = User.objects(id=current_user["id"]).first()

        chat_members = []
        for member in members:
            user = User.objects(name=member["label"], email=member["value"]).first()
            chat_members.append(user)

        chat_members.append(cur_user)

        try:
            new_chat = ChatCreation.create_new(title=title, members=chat_members).save()
        except:
            return {"success": False, "message": "Chat with same users already exist"}

        return {"success": True, "message": "New chat created, title: {}, members: {}".format(new_chat.title, new_chat.members),
                "chat": {"members": ",".join([m.name for m in chat_members]),
                         "title": new_chat.title, "id": str(new_chat.id)}}

    @login_required
    def get(self):
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

        print("users ", users)

        #return [{"label": user.name, "value": user.email}]

        return users


class UserLogoutAccess(Resource):
    @login_required
    def post(self):
        print("user logout")

        #@TODO: remove cookie

        logout_user()
        session.clear()

        # try:
        #     revoked_token = RevokedTokens(jti=jti)
        #     revoked_token.save()
        #     return {'message': 'Access token has been revoked'}
        # except:
        #     return {'message': 'Something went wrong'}, 500

