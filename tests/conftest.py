import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import create_app
from flask import json


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def get_auth_token(client, username, password):
    payload = {
        "username": username,
        "password": password
    }

    response = client.post('/auth/login', data=json.dumps(payload), content_type='application/json')
    data = json.loads(response.data)
    return data['token']