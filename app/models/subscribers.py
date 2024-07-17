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
        db = current_app.mongo.client['bigvu']
        subscribers_collection = db['subscribers']

        if subscribers_collection.find_one(
                {"subscriber_id": ObjectId(subscriber_id), "subscribed_to_id": ObjectId(subscribed_to_id)}):
            return None, "Already subscribed to this user."

        subscription = Subscribers(subscriber_id, subscribed_to_id)
        result = subscribers_collection.insert_one(subscription.to_dict())
        subscription.subscription_id = result.inserted_id
        return subscription, "Subscription created successfully."

    @staticmethod
    def get_subscriptions(subscriber_id):
        db = current_app.mongo.client['bigvu']
        subscribers_collection = db['subscribers']
        subscriptions = subscribers_collection.find({"subscriber_id": ObjectId(subscriber_id)})
        subscribed_to_ids = [subscription['subscribed_to_id'] for subscription in subscriptions]
        return subscribed_to_ids