from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
jwt = JWTManager()
db = SQLAlchemy()


def create_app(config_class="config.DevelopmentConfig"):
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
        }
    }

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v2/',
        authorizations=authorizations,
        security='Bearer Auth'
    )

    from part4.BE.app.api.v2.users     import api as users_ns
    from part4.BE.app.api.v2.amenities import api as amenities_ns
    from part4.BE.app.api.v2.places    import api as places_ns
    from part4.BE.app.api.v2.reviews   import api as reviews_ns
    from part4.BE.app.api.v2.bookings  import api as bookings_ns
    from part4.BE.app.api.v2.auth      import api as auth_ns

    api.add_namespace(users_ns,     path='/api/v2/users')
    api.add_namespace(amenities_ns, path='/api/v2/amenities')
    api.add_namespace(places_ns,    path='/api/v2/places')
    api.add_namespace(reviews_ns,   path='/api/v2/reviews')
    api.add_namespace(bookings_ns,  path='/api/v2/bookings')
    api.add_namespace(auth_ns,      path='/api/v2/auth')

    return app