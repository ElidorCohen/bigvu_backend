from flask_restx import Api
from app.routes import auth_ns as auth_namespace

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


