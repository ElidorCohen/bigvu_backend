from flask import json


def test_login_success(client):
    payload = {
        "username": "Elidor00000",
        "password": "Elidor00000"
    }

    client.post('/auth/register', data=json.dumps(payload), content_type='application/json')

    response = client.post('/auth/login', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['msg'] == "Login successful"
    assert 'token' in data


def test_login_invalid_input(client):
    test_cases = [
        (
        {"username": "Elidor00000", "password": "Elidor"}, "Username and password must be at least 8 characters long."),
        ({"username": "Elidor00000", "password": "wrongpassword1"}, "Invalid username or password")
    ]

    for payload, expected_message in test_cases:
        if payload['username'] == "Elidor00000" and payload['password'] != "wrongpassword":
            client.post('/auth/register', data=json.dumps(payload), content_type='application/json')

        response = client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['msg'] == expected_message


def test_login_missing_fields(client):
    test_cases = [
        ({"username": "Elidor00000", "password": ""}, "Password is required"),
        ({"username": "", "password": "Elidor00000"}, "Username is required"),
        ({"username": "", "password": ""}, "Username and password are required")
    ]

    for payload, expected_message in test_cases:
        response = client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['msg'] == expected_message