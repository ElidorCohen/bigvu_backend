import jwt
from bson import ObjectId
from flask import request, Response, current_app
from flask_restx import Namespace, Resource, fields
import json
from app.models.notes import Note
from app.models.subscribers import Subscribers
from app.models.user import User
from app.services.authentication import AuthenticationServices, token_required
from app.validators import validate_register_input


auth_ns = Namespace('auth', description='Authentication Operations')
note_ns = Namespace('notes', description='Notes Operations')
subscribe_ns = Namespace('subscribe', description='Subscription Operations')
user_ns = Namespace('users', description='User operations')


user_model = auth_ns.model('User', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The user password'),
})

note_model = note_ns.model('Note', {
    'title': fields.String(required=True, description='The title of the note'),
    'body': fields.String(required=True, description='The body of the note'),
})


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model, validate=True)
    @auth_ns.response(200, 'User registered successfully')
    @auth_ns.response(400, 'Bad request')
    def post(self):
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"msg": "Username and password are required"}, 400

        # Validate input:
        is_valid, error_message = validate_register_input(username, password)
        if not is_valid:
            return {"msg": error_message}, 400

        user, message = AuthenticationServices.register_user(username, password)
        if user:
            return {"msg":message,"user":user}, 200
        else:
            return {"msg":message}, 400


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model, validate=True)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(400, 'Bad request')
    def post(self):
        """Login a user"""
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return {"msg": "Username and password are required"}, 400

        user = AuthenticationServices.authenticate_user(username, password)
        if user:
            token = AuthenticationServices.create_jwt_token(user)
            return {"msg": "Login successful", "token": token}, 200
        else:
            return {"msg": "Invalid username or password"}, 400


@auth_ns.route('/private')
class Private(Resource):
    @auth_ns.doc(security='Bearer Auth')
    @auth_ns.doc(responses={200: 'Access granted.'})
    @token_required
    def get(self):
        return {"message": "Access granted."}, 200


@auth_ns.route('/profile')
class Profile(Resource):
    @auth_ns.doc(description='Retrieve user profile. Requires a valid JWT token.',
                 responses={
                     200: 'Profile retrieved successfully',
                     401: 'Unauthorized',
                     403: 'Token is missing!'
                 },
                 security='Bearer Auth')
    @token_required
    def get(self):
        """Retrieve user profile"""
        token = request.headers.get('Authorization').split()[1]
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = data['id']

        user, latest_sentiment = User.find_by_id(user_id)
        if user:
            profile = {
                "username": user.username,
                "user_id": user.id,
                "latest_sentiment": latest_sentiment
            }
            return profile, 200
        else:
            return {"msg": "User not found."}, 404


@note_ns.route('/create_note')
class CreateNote(Resource):
    @note_ns.expect(note_model, validate=True)
    @note_ns.doc(description='Create a new note. Requires a valid JWT token.',
                 responses={
                     200: 'Note created successfully',
                     400: 'Bad request',
                     401: 'Unauthorized',
                     403: 'Token is missing!'
                 },
                 security='Bearer Auth')
    @token_required
    def post(self):
        """Create a new note"""
        data = request.json
        title = data.get('title')
        body = data.get('body')

        if not title or not body:
            return {"msg": "Title and body are required"}, 400

        token = request.headers.get('Authorization').split()[1]
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['id']

        note = Note.create_note(title, body, user_id)
        print("Second note print: ", note)
        return {"msg": "Note created successfully", "note": str(note)}, 200


@subscribe_ns.route('/<id>')
class Subscribe(Resource):
    @subscribe_ns.doc(description='Subscribe to a user\'s notes. Requires a valid JWT token.',
                      params={'id': 'The ID of the user to subscribe to'},
                      responses={
                          200: 'Subscription created successfully',
                          400: 'Bad request',
                          401: 'Unauthorized',
                          403: 'Token is missing!'
                      },
                      security='Bearer Auth')
    @token_required
    def post(self, id):
        """Subscribe to a user's notes"""
        token = request.headers.get('Authorization').split()[1]
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        subscriber_id = decoded_token['id']

        subscription, message = Subscribers.subscribe_to(subscriber_id, id)
        if subscription:
            return {"msg": message, "subscription_id": str(subscription.subscription_id)}, 200
        else:
            return {"msg": message}, 400


@note_ns.route('/retrieve_notes')
class RetrieveNotes(Resource):
    @note_ns.doc(
        description='Retrieve notes created by the authenticated user and users they are subscribed to. Requires a valid JWT token.',
        responses={
            200: 'Notes retrieved successfully',
            401: 'Unauthorized',
            403: 'Token is missing!',
            404: 'No notes found'
        },
        security='Bearer Auth')
    @token_required
    def get(self):
        """Retrieve notes"""
        token = request.headers.get('Authorization').split()[1]
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['id']

        subscribed_to_ids = Subscribers.get_subscriptions(user_id)

        user_ids = [user_id] + subscribed_to_ids
        notes = Note.get_notes(user_ids)

        if notes:
            return {"notes": [note.to_dict(convert_id=True, convert_time=True) for note in notes]}, 200
        else:
            return {"msg": "No notes found."}, 404


@note_ns.route('/<id>')
class RetrieveNoteById(Resource):
    @note_ns.doc(description='Retrieve a specific note by ID. Requires a valid JWT token.',
                 params={'id': 'The ID of the note to retrieve'},
                 responses={
                     200: 'Note retrieved successfully',
                     401: 'Unauthorized',
                     403: 'Token is missing!',
                     404: 'Note not found'
                 },
                 security='Bearer Auth')
    @token_required
    def get(self, id):
        """Retrieve a specific note by ID"""
        token = request.headers.get('Authorization').split()[1]
        decoded_token = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        user_id = decoded_token['id']

        note, error = Note.get_note_by_id(id)
        if error:
            return {"msg": error}, 404

        subscribed_to_ids = Subscribers.get_subscriptions(user_id)
        if str(note.user_id) == user_id or ObjectId(note.user_id) in subscribed_to_ids:
            return {"note": note.to_dict(convert_id=True, convert_time=True)}, 200
        else:
            return {"msg": "You are not authorized to view this note. Subscribe to user's note first."}, 401


@user_ns.route('/')
class ListAllUsers(Resource):
    @user_ns.doc(description='List all users in the system. Requires a valid JWT token.',
                 responses={
                     200: 'Users retrieved successfully',
                     401: 'Unauthorized',
                     403: 'Token is missing!'
                 },
                 security='Bearer Auth')
    @token_required
    def get(self):
        """List all users"""
        users = User.get_all_users()
        return {"users": users}, 200