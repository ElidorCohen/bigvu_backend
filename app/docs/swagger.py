from flask_restx import Api
from app.routes import auth_ns as auth_namespace
from app.routes import note_ns as note_namespace
from app.routes import subscribe_ns as subscribe_namespace
from app.routes import user_ns as user_namespace


api = Api(
    title='BIGVU Task API',
    version='1.0',
    description='API documentation for BIGVU Task',
    doc='/swagger/',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        },
    }
)

api.add_namespace(auth_namespace, path='/auth')
api.add_namespace(note_namespace, path='/notes')
api.add_namespace(subscribe_namespace, path='/subscribe')
api.add_namespace(user_namespace, path='/users')



