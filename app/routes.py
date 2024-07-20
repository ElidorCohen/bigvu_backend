from bson import ObjectId
from flask import request
from flask_restx import Resource
from app.models.notes import Note
from app.models.subscribers import Subscribers
from app.models.user import User
from app.services.authentication import AuthenticationServices, token_required
from app.validators import validate_register_login_input, check_username_password_provided
import logging
from app.websocket.emit_controller import notify_subscribers
from app.models.api_models import auth_ns, note_ns, subscribe_ns, user_ns, user_model, note_model


@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(user_model, validate=True)
    @auth_ns.doc(description='Register a new user',
                 responses={
                     201: 'User registered successfully',
                     400: 'Bad request'
                 },
                 )
    def post(self):
        """Register a new user"""
        data = request.json
        username = data.get('username')
        password = data.get('password')

        is_provided, error_message = check_username_password_provided(username, password)
        if not is_provided:
            return {"msg": error_message}, 400

        is_valid, error_message = validate_register_login_input(username, password)
        if not is_valid:
            return {"msg": error_message}, 400

        user, message = User.register_user(username, password)
        if user:
            return {"msg": message, "user": user}, 201
        else:
            return {"msg": message}, 400


@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(user_model, validate=True)
    @auth_ns.doc(description='Login a user',
                 responses={
                     200: 'Login successful',
                     400: 'Bad request'
                 })
    def post(self):
        """Login a user"""
        data = request.json
        username = data.get('username')
        password = data.get('password')

        is_provided, error_message = check_username_password_provided(username, password)
        if not is_provided:
            return {"msg": error_message}, 400

        is_valid, error_message = validate_register_login_input(username, password)
        if not is_valid:
            return {"msg": error_message}, 400

        user = AuthenticationServices.authenticate_user(username, password)
        if user:
            token = AuthenticationServices.create_jwt_token(user)
            return {"msg": "Login successful", "token": token}, 200
        else:
            return {"msg": "Invalid username or password"}, 400


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
        user_id = AuthenticationServices.get_user_id_from_token()

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
                     201: 'Note created successfully',
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

        user_id = AuthenticationServices.get_user_id_from_token()

        note = Note.create_note(title, body, user_id)

        notify_subscribers(note, user_id)

        return {"msg": "Note created successfully", "note": str(note.note_id)}, 201


@subscribe_ns.route('/<id>')
class Subscribe(Resource):
    @subscribe_ns.doc(description='Subscribe to a user\'s notes. Requires a valid JWT token.',
                      params={'id': 'The ID of the user to subscribe to'},
                      responses={
                          201: 'Subscription created successfully',
                          400: 'Bad request',
                          401: 'Unauthorized',
                          403: 'Token is missing!'
                      },
                      security='Bearer Auth')
    @token_required
    def post(self, id):
        """Subscribe to a user's notes"""
        subscriber_id = AuthenticationServices.get_user_id_from_token()

        subscription, message = Subscribers.subscribe_to(subscriber_id, id)
        if subscription:
            return {"msg": message, "subscription_id": str(subscription.subscription_id)}, 201
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
        user_id = AuthenticationServices.get_user_id_from_token()

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
        user_id = AuthenticationServices.get_user_id_from_token()

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
                     403: 'Token is missing!',
                     400: 'Error accessing the database'
                 },
                 security='Bearer Auth')
    @token_required
    def get(self):
        """List all users"""
        try:
            users = User.get_all_users()
            return {"users": users}, 200
        except Exception as e:
            logging.error(f"Error accessing the database: {str(e)}")
            return {"msg": "Error accessing the database"}, 400
