from flask import json
import jwt
from tests.conftest import get_auth_token
from config import config


def decode_token(token):
    decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token['id']
    return user_id


def test_subscribe_success(client):
    username1 = "Elidor00000"
    password1 = "Elidor00000"
    username2 = "UserToSubscribe1"
    password2 = "UserToSubscribe123"

    client.post('/auth/register', data=json.dumps({"username": username2, "password": password2}), content_type='application/json')

    token = get_auth_token(client, username1, password1)

    response = client.post('/auth/login', data=json.dumps({"username": username2, "password": password2}), content_type='application/json')
    print(response.data)
    second_user_token = json.loads(response.data)['token']
    second_user_id = decode_token(second_user_token)

    response = client.post(f'/subscribe/{second_user_id}', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    data = json.loads(response.data)
    assert data['msg'] == "Subscription created successfully"
    assert 'subscription_id' in data


def test_subscribe_self(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)
    user_id = decode_token(token)

    response = client.post(f'/subscribe/{user_id}', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['msg'] == "Use can't subscribe to himself."


def test_subscribe_invalid_id(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)

    invalid_id = "thisisnotavalidid"
    response = client.post(f'/subscribe/{invalid_id}', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['msg'] == "Invalid ID provided"


def test_subscribe_unauthorized(client):
    valid_id = "669a8efff2da33e9a779ce89"  # valid user ID from  database @Elidor00000

    response = client.post(f'/subscribe/{valid_id}')

    assert response.status_code == 403

    data = json.loads(response.data)
    assert data['message'] == "Token is missing!"