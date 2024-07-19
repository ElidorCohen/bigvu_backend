from flask_restx import fields, Namespace

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
