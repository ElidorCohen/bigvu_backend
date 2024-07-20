from flask import json
from tests.conftest import get_auth_token


def test_profile_success(client, user_credentials):
    token = get_auth_token(client, user_credentials['username'], user_credentials['password'])

    response = client.get('/auth/profile', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['username'] == user_credentials['username']
    assert 'user_id' in data
    assert 'latest_sentiment' in data


def test_profile_unauthorized(client):
    response = client.get('/auth/profile')

    assert response.status_code == 403

    data = json.loads(response.data)
    assert data['message'] == 'Token is missing!'


def test_profile_invalid_token(client):
    invalid_token = "thisisnotavalidtoken"
    response = client.get('/auth/profile', headers={"Authorization": f"Bearer {invalid_token}"})

    assert response.status_code == 401

    data = json.loads(response.data)
    assert data['message'] == 'Token is invalid!'