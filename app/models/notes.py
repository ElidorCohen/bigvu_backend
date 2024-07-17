from flask import current_app
from datetime import datetime
from bson import ObjectId

class Note:
    def __init__(self, title, body, user_id, note_id=None, created_at=None, updated_at=None):
        self.title = title
        self.body = body
        self.user_id = user_id
        self.note_id = note_id
        self.created_at = created_at if created_at else datetime.utcnow()
        self.updated_at = updated_at if updated_at else datetime.utcnow()

    def to_dict(self):
        return {
            "title": self.title,
            "body": self.body,
            "user_id": ObjectId(self.user_id),
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def create_note(title, body, user_id):
        db = current_app.mongo.client['bigvu']
        notes_collection = db['notes']
        note = Note(title, body, user_id)
        result = notes_collection.insert_one(note.to_dict())
        print(f"Note created: {result.inserted_id}")
        return result.inserted_id
