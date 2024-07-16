from app.models.user import User
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app


class AuthenticationServices:
    @staticmethod
    def register_user(username, password):
        user, message = User.create_user(username, password)
        if user:
            return user, message
        else:
            return None, message

    @staticmethod
    def authenticate_user(username, password):
        user = User.find_by_username(username)
        if user and User.verify_password(user.hashed_password, password):
            return user
        return False

    @staticmethod
    def create_jwt_token(user):
        expiration = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode({
            'id': user.id,
            'username': user.username,
            'exp': expiration
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        return token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {'message': 'Token is missing!'}, 403
        try:
            scheme, token = token.split()
            if scheme != 'Bearer':
                return {'message': 'Token format is invalid!'}, 401
        except ValueError:
            return {'message': 'Token format is invalid!'}, 401
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            print(f"Decoded token data: {data}")
        except jwt.ExpiredSignatureError:
            return {'message': 'Token has expired!'}, 401
        except jwt.InvalidTokenError:
            return {'message': 'Token is invalid!'}, 401
        return f(*args, **kwargs)
    return decorated