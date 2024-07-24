import logging
import bcrypt
from bson import ObjectId
from flask import current_app


class User:
    def __init__(self, username, hashed_password, user_id=None, latest_sentiment=None):
        self.username = username
        self.hashed_password = hashed_password
        self.id = user_id
        self.latest_sentiment = latest_sentiment

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

        try:
            if users_collection.find_one({"username": username}):
                return None, "User already exists."
        except Exception as e:
            logging.error(f"Error checking if user exists: {str(e)}")
            return None, "Failed to check if user exists."

        try:
            hashed_password = User.hash_password(password)
            user = {
                "username": username,
                "hashed_password": hashed_password
            }
            result = users_collection.insert_one(user)
            return {"id": str(result.inserted_id), "username": username}, "User registered successfully."
        except Exception as e:
            logging.error(f"Error inserting new user: {str(e)}")
            return None, "Failed to register user."

    @staticmethod
    def register_user(username, password):
        user, message = User.create_user(username, password)
        if user:
            return user, message
        else:
            return None, message

    @staticmethod
    def find_by_username(username):
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']
        try:
            user_data = users_collection.find_one({"username": username})
            if user_data:
                return User(user_data['username'], user_data['hashed_password'], str(user_data['_id']))
            return None
        except Exception as e:
            logging.error(f"Error finding user by username: {str(e)}")
            return None

    @staticmethod
    def find_by_id(user_id):
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']

        try:
            user_data = users_collection.find_one({"_id": ObjectId(user_id)})
            if user_data:
                user = User(user_data['username'], user_data['hashed_password'], str(user_data['_id']),
                            user_data.get('latest_sentiment'))
                return user
            return None
        except Exception as e:
            logging.error(f"Error finding user by id: {str(e)}")
            return None

    @staticmethod
    def get_all_users():
        db = current_app.mongo.client['bigvu']
        users_collection = db['users']
        try:
            users = users_collection.find({}, {"username": 1})
            return [{"_id": str(user["_id"]), "username": user["username"]} for user in users]
        except Exception as e:
            logging.error(f"Error accessing the database: {str(e)}")
