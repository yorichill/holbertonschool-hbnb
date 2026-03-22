from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()

def create_app(config_class="config.DevelopmentConfig"):
    # Initialisation de l'application Flask
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': "Type 'Bearer <token>' to authorize."
        }
    }

    # Configuration de l'API REST avec Flask-RESTX
    # La documentation Swagger est accessible à /api/v1/
    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/',
        authorizations=authorizations,
        security='Bearer Auth'
    )

    # Enregistrement des namespaces (routes) de chaque ressource
    # Chaque namespace regroupe les endpoints liés à une entité métier

    from app.api.v1.users import api as users_ns
    api.add_namespace(users_ns, path='/api/v1/users')           # Gestion des utilisateurs

    from app.api.v1.places import api as places_ns
    api.add_namespace(places_ns,    path='/api/v1/places')      # Gestion des logements

    from app.api.v1.amenities import api as amenities_ns
    api.add_namespace(amenities_ns, path='/api/v1/amenities')   # Gestion des équipements

    from app.api.v1.reviews import api as reviews_ns
    api.add_namespace(reviews_ns,   path='/api/v1/reviews')     # Gestion des avis

    from app.api.v1.bookings import api as bookings_ns
    api.add_namespace(bookings_ns,  path='/api/v1/bookings')    # Gestion des réservations

    from app.api.v1.auth import api as auth_ns
    api.add_namespace(auth_ns, path='/api/v1/auth')  # Authentification

    return app  # Retourne l'instance de l'application configurée
