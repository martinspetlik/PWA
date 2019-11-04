from flask_restful import Resource
from flask import request, jsonify
from server.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (create_access_token, create_refresh_token, jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

from mongoengine.errors import ValidationError
from server.models.revoked_tokens import RevokedTokens


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


class UserLogin(Resource):
    def get(self):
        print("landing page")

    def post(self):
        print("LOGIN")

        email = request.get_json()['email']
        password = request.get_json()['password']

        print("email ", email)
        print("password ", password)

        # remember = True if request.form.get('remember') else False

        user = User.objects(email=email).first()

        print("Login user ", user)
        print("login user type ", type(user))

        if user:
            if check_password_hash(user.password, password):
                access_token = create_access_token(identity={'name': user.name, 'email': user.email})
                refresh_token = create_refresh_token(identity={'name': user.name, 'email': user.email})
                return {
                    'success': True,
                    'message': 'Logged in as {}'.format(user.name),
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            else:
                return {"success": False, 'message': 'Wrong credentials'}
        else:
            result = {"success": False, "message": "Invalid user email"}

        # access token has 15 minutes lifetime
        # print("access token ", access_token)

        return result


class UserProfile(Resource):
    @jwt_required
    def get(self):
        print("PROFILE")
        current_user = get_jwt_identity()

        print("current user ", current_user)

        return {"name": current_user['name'], "email": current_user['email']}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        print("user logout")
        jti = get_raw_jwt()['jti']

        try:
            revoked_token = RevokedTokens(jti=jti)
            revoked_token.save()
            return {'message': 'Access token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedTokens(jti=jti)
            revoked_token.save()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}
