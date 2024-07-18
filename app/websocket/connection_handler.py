import logging
from flask import Blueprint, request
from flask_socketio import join_room
from app.services.authentication import AuthenticationServices
from app.websocket.emit_controller import socketio

ui = Blueprint('ui', __name__)


@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        return False
    try:
        user_id = AuthenticationServices.get_user_id_from_token()
        join_room(user_id)
        logging.info(f"User {user_id} joined room")
    except Exception as e:
        logging.error(f"Failed to authenticate user: {e}")
        return False
