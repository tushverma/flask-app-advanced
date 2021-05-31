from flask_restful import Resource
from flask import request
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt,
    fresh_jwt_required,
)
from models.user import UserModel
from models.confirmation import ConfirmationModel
from blacklist import BLACKLIST
from schemas.user import UserSchema
import traceback
from libs.mailgun import MailGunException

user_schema = UserSchema()


class UserRegister(Resource):
    @classmethod
    def post(cls):
        user = user_schema.load(request.get_json())
        if UserModel.find_by_username(user.username):
            return {"message": "A user with that username already exists."}, 400
        if UserModel.find_by_email(user.email):
            return {"message": "A user with that email already exists."}, 400
        try:
            user.save_to_db()
            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()
        except MailGunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()
            return {"message": "Failed to create user"}, 500
        return {"message": "Account created successfully, please check email"}, 201


class User(Resource):
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404
        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found."}, 404
        user.delete_from_db()
        return {"message": "User deleted."}, 200


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = user_schema.load(request.json, partial=('email',))

        user = UserModel.find_by_username(data.username)

        # this is what the `authenticate()` function did in security.py
        if user and safe_str_cmp(user.password, data.password):
            confirmation = user.most_recent_confirmation
            # identity= is what the identity() function did in security.py—now stored in the JWT
            if confirmation and confirmation.confirmed:
                access_token = create_access_token(identity=user.id, fresh=True)
                refresh_token = create_refresh_token(user.id)
                return {"access_token": access_token, "refresh_token": refresh_token}, 200
            else:
                return {"message": "You have not confirmed your email."}, 400

        return {"message": "Invalid credentials!"}, 401


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        jti = get_raw_jwt()["jti"]  # jti is "JWT ID", a unique identifier for a JWT.
        user_id = get_jwt_identity()
        BLACKLIST.add(jti)
        return {"message": "User <id={}> successfully logged out.".format(user_id)}, 200


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}, 200


class SetPassword(Resource):
    @classmethod
    @fresh_jwt_required
    def post(cls):
        user_json = request.json
        user_data = user_schema.load(user_json)
        user = UserModel.find_by_username(user_data.username)
        if not user:
            return {"message": "User not found"}, 400
        user.password = user_data.password
        user.save_to_db()
        return {"message": "user created successfully"}, 200
