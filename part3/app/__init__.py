from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
# NOUVEAU : On importe JWTManager
from flask_jwt_extended import JWTManager
from config import config 

bcrypt = Bcrypt()
# NOUVEAU : On instancie le gestionnaire de tokens
jwt = JWTManager()

from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.users import api as users_ns
# NOUVEAU : On importe notre nouvelle route auth
from app.api.v1.auth import api as auth_ns

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    bcrypt.init_app(app)
    # NOUVEAU : On lie JWT à notre application
    jwt.init_app(app)

    api = Api(app, version='1.0', title='HBnB API', description='HBnB Application API', doc='/api/v1/')

    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(users_ns, path='/api/v1/users')
    # NOUVEAU : On ajoute la route à Swagger
    api.add_namespace(auth_ns, path='/api/v1/auth')
    
    return app