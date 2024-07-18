from flask_socketio import SocketIO
import logging
from app.models.subscribers import Subscribers


socketio = SocketIO()


def notify_subscribers(note, user_id):
    socketio.emit('new_note', {'note': note.to_dict()}, room=user_id)
    subscribers = Subscribers.get_subscribers_for_user(user_id)
    for subscriber in subscribers:
        socketio.emit('new_note', {'note': note.to_dict()}, room=subscriber)
        logging.info(
            f"User {subscriber} received a real-time update: new note created by User {user_id}, note: {note.to_dict(convert_time=True, convert_id=True)}")