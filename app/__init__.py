from flask import Flask
from config import config
from app.db import init_db
from app.docs.swagger import api
from app.websocket.connection_handler import ui
from app.websocket.emit_controller import socketio
import logging


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    logging.basicConfig(level=logging.INFO)
    init_db(app)
    api.init_app(app)
    socketio.init_app(app)
    app.register_blueprint(ui)
    return app
