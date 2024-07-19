from flask import json
from tests.conftest import get_auth_token


def test_list_all_users_success(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)

    headers = {"Authorization": f"Bearer {token}"}

    response = client.get('/users/', headers=headers)

    assert response.status_code == 200

    data = json.loads(response.data)
    assert "users" in data
    assert len(data["users"]) >= 3 # We have 3 users in the database


def test_list_all_users_missing_token(client):
    response = client.get('/users/')

    assert response.status_code == 403

    data = json.loads(response.data)
    assert data['message'] == "Token is missing!"
