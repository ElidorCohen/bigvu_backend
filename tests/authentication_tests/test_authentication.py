import jwt
from flask import current_app
from app.models.user import User
from app.services.authentication import AuthenticationServices


def test_authentication_user_success(client, user_credentials):
    authenticated_user = AuthenticationServices.authenticate_user(user_credentials['username'], user_credentials['password'])
    assert authenticated_user is not False
    assert authenticated_user.username == user_credentials['username']


def test_authenticate_user_failure(client):
    authenticated_user = AuthenticationServices.authenticate_user("NonExistentUser", "WrongPassword")
    assert authenticated_user is False


def test_create_jwt_token(client, user_credentials):
    user = User.find_by_username(user_credentials['username'])
    token = AuthenticationServices.create_jwt_token(user)
    assert token is not None
    decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    assert decoded_token['username'] == user.username
