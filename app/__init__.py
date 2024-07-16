from flask import Flask
from config import config
from app.db import init_db
from app.swagger import api


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    init_db(app)
    api.init_app(app)
    return app
