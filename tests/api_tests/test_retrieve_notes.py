from tests.conftest import get_auth_token
from flask import json


def test_retrieve_notes_success(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get('/notes/retrieve_notes', headers=headers)

    assert response.status_code == 200

    data = json.loads(response.data)
    assert "notes" in data
    assert isinstance(data["notes"], list)


def test_retrieve_notes_no_notes(client):
    username = "userNoNotes1"
    password = "userNoNotes1"

    client.post('/auth/register', data=json.dumps({"username": username, "password": password}), content_type='application/json')

    token = get_auth_token(client, username, password)

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = client.get('/notes/retrieve_notes', headers=headers)

    assert response.status_code == 404

    data = json.loads(response.data)
    assert data['msg'] == "No notes found."


def test_retrieve_notes_missing_token(client):
    response = client.get('/notes/retrieve_notes')

    assert response.status_code == 403

    data = json.loads(response.data)
    assert data['message'] == "Token is missing!"


def test_retrieve_notes_invalid_token(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)
    invalid_token = token + "invalid"

    headers = {
        "Authorization": f"Bearer {invalid_token}"
    }

    response = client.get('/notes/retrieve_notes', headers=headers)

    assert response.status_code == 401

    data = json.loads(response.data)
    assert data['message'] == "Token is invalid!"