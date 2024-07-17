import bcrypt
from bson import ObjectId
from flask import current_app


class User:
    def __init__(self, username, hashed_password, user_id=None):
        self.username = username
        self.hashed_password = hashed_password
        self.id = user_id

    @staticmethod
    def hash_password(password):
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(hashed_password, password):
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_user(username, password):
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']

        if users_collection.find_one({"username": username}):
            return None, "User already exists."

        hashed_password = User.hash_password(password)
        user = {
            "username": username,
            "hashed_password": hashed_password
        }
        result = users_collection.insert_one(user)
        return {"id": str(result.inserted_id), "username": username}, "User registered successfully."

    @staticmethod
    def find_by_username(username):
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']
        user_data = users_collection.find_one({"username": username})
        if user_data:
            return User(user_data['username'], user_data['hashed_password'], str(user_data['_id']))
        return None

    @staticmethod
    def find_by_id(user_id):
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']
        notes_collection = db['notes']

        user_data = users_collection.find_one({"_id": ObjectId(user_id)})
        if user_data:
            user = User(user_data['username'], user_data['hashed_password'], str(user_data['_id']))

            latest_note = notes_collection.find({"user_id": ObjectId(user_id)}).sort("created_at", -1).limit(1)
            latest_sentiment = None
            latest_note_list = list(latest_note)  # Convert cursor to list to check for results
            if latest_note_list:
                latest_sentiment = latest_note_list[0].get("sentiment", None)

            return user, latest_sentiment
        return None, None

    @staticmethod
    def get_all_users():
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']
        users = users_collection.find({}, {"username": 1})
        return [{"_id": str(user["_id"]), "username": user["username"]} for user in users]