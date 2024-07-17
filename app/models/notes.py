from bson.errors import InvalidId
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

    def to_dict(self, convert_id=False, convert_time=False):
        return {
            "title": self.title,
            "body": self.body,
            "user_id": str(self.user_id) if convert_id else ObjectId(self.user_id),
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if convert_time else self.created_at,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if convert_time else self.updated_at
        }

    @staticmethod
    def create_note(title, body, user_id):
        db = current_app.mongo.client['bigvu']
        notes_collection = db['notes']
        note = Note(title, body, user_id)
        result = notes_collection.insert_one(note.to_dict())
        print(f"Note created: {result.inserted_id}")
        return result.inserted_id

    @staticmethod
    def get_notes(user_ids):
        db = current_app.mongo.client['bigvu']
        notes_collection = db['notes']
        notes = notes_collection.find({"user_id": {"$in": [ObjectId(user_id) for user_id in user_ids]}})
        return [Note(
            title=note["title"],
            body=note["body"],
            user_id=note["user_id"],
            note_id=note["_id"],
            created_at=note["created_at"],
            updated_at=note["updated_at"]
        ) for note in notes]

    @staticmethod
    def get_note_by_id(note_id):
        db = current_app.mongo.client['bigvu']
        notes_collection = db['notes']
        try:
            note = notes_collection.find_one({"_id": ObjectId(note_id)})
        except InvalidId:
            return None, "Invalid note ID."

        if note:
            return Note(
                title=note["title"],
                body=note["body"],
                user_id=note["user_id"],
                note_id=note["_id"],
                created_at=note["created_at"],
                updated_at=note["updated_at"]
            ), None
        return None, "Note not found."