from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from config import config 

bcrypt = Bcrypt()
jwt = JWTManager()

from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.users import api as users_ns
from app.api.v1.auth import api as auth_ns

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bcrypt.init_app(app)
    jwt.init_app(app)

    # 1. On définit la stratégie de sécurité pour Swagger
    authorizations = {
        'bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Tapez 'Bearer <VOTRE_TOKEN>' pour vous authentifier. N'oubliez pas l'espace après Bearer."
        }
    }

    # 2. On ajoute les authorizations et la sécurité globale à l'API
    api = Api(
        app, 
        version='1.0', 
        title='HBnB API', 
        description='HBnB Application API', 
        doc='/api/v1/',
        authorizations=authorizations,
        security='bearer'
    )

    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(auth_ns, path='/api/v1/auth')
    
    return app