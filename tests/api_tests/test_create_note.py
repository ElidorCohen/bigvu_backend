from flask import json
from tests.conftest import get_auth_token


def test_create_note_success(client, user_credentials):
    note_payload = {
        "title": "Test Note",
        "body": "This is a test note.1"
    }

    token = get_auth_token(client, user_credentials['username'], user_credentials['password'])

    response = client.post('/notes/create_note', data=json.dumps(note_payload), content_type='application/json', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 201

    data = json.loads(response.data)
    assert data['msg'] == "Note created successfully"
    assert 'note' in data


def test_create_note_missing_title(client, user_credentials):
    note_payload = {
        "title": "",
        "body": "This is a test note without a title."
    }

    token = get_auth_token(client, user_credentials['username'], user_credentials['password'])

    response = client.post('/notes/create_note', data=json.dumps(note_payload), content_type='application/json', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['msg'] == "Title and body are required"


def test_create_note_missing_body(client, user_credentials):
    note_payload = {
        "title": "Test Note",
        "body": ""
    }

    token = get_auth_token(client, user_credentials['username'], user_credentials['password'])

    response = client.post('/notes/create_note', data=json.dumps(note_payload), content_type='application/json', headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['msg'] == "Title and body are required"


def test_create_note_unauthorized(client):
    note_payload = {
        "title": "Test Note",
        "body": "This is a test note."
    }

    response = client.post('/notes/create_note', data=json.dumps(note_payload), content_type='application/json')

    assert response.status_code == 403

    data = json.loads(response.data)
    assert data['message'] == "Token is missing!"