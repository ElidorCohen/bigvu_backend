import jwt
from flask import request, Response, current_app
from flask_restx import Namespace, Resource, fields
import json
from app.models.notes import Note
from app.models.user import User
from app.services.authentication import AuthenticationServices, token_required
from app.validators import validate_register_input


auth_ns = Namespace('auth', description='Authentication Operations')
note_ns = Namespace('notes', description='Notes Operations')

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

        user = User.find_by_id(user_id)
        if user:
            return {"username": user.username, "user_id": user.id}, 200
        else:
            return {"msg": "User not found."}, 404


@note_ns.route('/')
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