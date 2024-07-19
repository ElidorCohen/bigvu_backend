import logging

from flask import current_app
from bson import ObjectId
from datetime import datetime


class Subscribers:
    def __init__(self, subscriber_id, subscribed_to_id, subscription_id=None):
        self.subscriber_id = subscriber_id
        self.subscribed_to_id = subscribed_to_id
        self.subscription_id = subscription_id
        self.created_at = datetime.utcnow()

    def to_dict(self):
        return {
            "subscriber_id": ObjectId(self.subscriber_id),
            "subscribed_to_id": ObjectId(self.subscribed_to_id),
            "created_at": self.created_at
        }

    @staticmethod
    def subscribe_to(subscriber_id, subscribed_to_id):
        if subscriber_id == subscribed_to_id:
            return None, "Use can't subscribe to himself."

        db = current_app.mongo.client['bigvu']
        subscribers_collection = db['subscribers']
        try:
            if subscribers_collection.find_one(
                    {"subscriber_id": ObjectId(subscriber_id), "subscribed_to_id": ObjectId(subscribed_to_id)}):
                return None, "Already subscribed to this user."
        except Exception as e:
            logging.error(f"Error checking subscription: {str(e)}")
            return None, "Invalid ID provided"

        try:
            subscription = Subscribers(subscriber_id, subscribed_to_id)
            result = subscribers_collection.insert_one(subscription.to_dict())
            subscription.subscription_id = result.inserted_id
            return subscription, "Subscription created successfully"
        except Exception as e:
            logging.error(f"Error creating subscription: {str(e)}")
            return None, "Failed to create subscription."

    @staticmethod
    def get_subscriptions(subscriber_id):
        db = current_app.mongo.client['bigvu']
        subscribers_collection = db['subscribers']
        try:
            subscriptions = subscribers_collection.find({"subscriber_id": ObjectId(subscriber_id)})
            subscribed_to_ids = [subscription['subscribed_to_id'] for subscription in subscriptions]
            return subscribed_to_ids
        except Exception as e:
            logging.error(f"Error accessing the database: {str(e)}")
            return []

    # Need to add try and except block here, lo lishkoah
    @staticmethod
    def get_subscribers_for_user(user_id):
        db = current_app.mongo.client['bigvu']
        subscribers_collection = db['subscribers']
        subscribers = subscribers_collection.find({"subscribed_to_id": ObjectId(user_id)})
        return [str(subscriber["subscriber_id"]) for subscriber in subscribers]
