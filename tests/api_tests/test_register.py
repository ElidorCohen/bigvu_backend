from flask import json


def test_register_success(client):
    payload = {
        "username": "TestUser199452",
        "password": "TestUser199452"
    }

    response = client.post('/auth/register', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 201

    data = json.loads(response.data)
    assert data['msg'] == "User registered successfully."
    assert 'user' in data
    assert 'id' in data['user']
    assert data['user']['username'] == payload['username']


def test_register_missing_fields(client):
    test_cases = [
        ({"username": "Elidor00000", "password": ""}, "Password is required"),
        ({"username": "", "password": "Elidor00000"}, "Username is required"),
        ({"username": "", "password": ""}, "Username and password are required")
    ]

    for payload, expected_message in test_cases:
        response = client.post('/auth/register', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['msg'] == expected_message


def test_register_invalid_input(client):
    payload = {
        "username": "Elidor",
        "password": "Elidor00000"
    }

    response = client.post('/auth/register', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 400

    data = json.loads(response.data)
    assert data['msg'] == "Username and password must be at least 8 characters long."
