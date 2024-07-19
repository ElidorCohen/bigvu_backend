from flask import json
from bson import ObjectId
from tests.conftest import get_auth_token


def test_retrieve_note_success(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)

    headers = {"Authorization": f"Bearer {token}"}
    note_payload = {"title": "Test Note", "body": "This is a test note."}
    response = client.post('/notes/create_note', data=json.dumps(note_payload), headers=headers,
                           content_type='application/json')
    note_id = json.loads(response.data)['note']

    response = client.get(f'/notes/{note_id}', headers=headers)

    assert response.status_code == 200

    data = json.loads(response.data)
    assert "note" in data
    assert data["note"]["_id"] == note_id


def test_retrieve_note_unauthorized(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)

    headers = {"Authorization": f"Bearer {token}"}
    note_payload = {"title": "Test Note", "body": "This is a test note."}
    response = client.post('/notes/create_note', data=json.dumps(note_payload), headers=headers,
                           content_type='application/json')
    note_id = json.loads(response.data)['note']

    other_username = "userNoNotes1"
    other_password = "userNoNotes1"
    client.post('/auth/register', data=json.dumps({"username": other_username, "password": other_password}),
                content_type='application/json')

    other_token = get_auth_token(client, other_username, other_password)
    other_headers = {"Authorization": f"Bearer {other_token}"}

    response = client.get(f'/notes/{note_id}', headers=other_headers)

    assert response.status_code == 401

    data = json.loads(response.data)
    assert data['msg'] == "You are not authorized to view this note. Subscribe to user's note first."


def test_retrieve_note_not_found(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)

    headers = {"Authorization": f"Bearer {token}"}

    non_existent_note_id = str(ObjectId())
    response = client.get(f'/notes/{non_existent_note_id}', headers=headers)

    assert response.status_code == 404

    data = json.loads(response.data)
    assert data['msg'] == "Note not found."


def test_retrieve_note_missing_token(client):
    response = client.get('/notes/123456789012345678901234')

    assert response.status_code == 403

    data = json.loads(response.data)
    assert data['message'] == "Token is missing!"


def test_retrieve_note_invalid_token(client):
    username = "Elidor00000"
    password = "Elidor00000"

    token = get_auth_token(client, username, password)
    invalid_token = token + "invalid"

    headers = {"Authorization": f"Bearer {invalid_token}"}

    response = client.get('/notes/123456789012345678901234', headers=headers)

    assert response.status_code == 401

    data = json.loads(response.data)
    assert data['message'] == "Token is invalid!"