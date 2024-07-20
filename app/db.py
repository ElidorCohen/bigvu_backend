from pymongo import MongoClient
import certifi


class SingletonDB:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SingletonDB, cls).__new__(cls)
        return cls._instance

    def __init__(self, app):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.client = MongoClient(app.config['MONGO_URI'], tlsCAFile=certifi.where())
            self.db = self.client.get_default_database()


def init_db(app):
    app.mongo = SingletonDB(app)
