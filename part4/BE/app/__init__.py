from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db     = SQLAlchemy()
bcrypt = Bcrypt()
jwt    = JWTManager()


def create_app(config_class='config.DevelopmentConfig'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # ── Extensions ────────────────────────────────────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    CORS(app, origins='http://localhost:8080', supports_credentials=True)

    # ── API ───────────────────────────────────────────────────────────────
    authorizations = {
        'Bearer Auth': {
            'type': 'apiKey',
            'in':   'header',
            'name': 'Authorization',
        }
    }

    api = Api(
        app,
        version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        prefix='/api/v1',
        doc='/api/v2/doc',
        authorizations=authorizations,
        security='Bearer Auth',
    )

    # ── Namespaces ────────────────────────────────────────────────────────
    from app.api.v2.auth      import api as auth_ns
    from app.api.v2.users     import api as users_ns
    from app.api.v2.places    import api as places_ns
    from app.api.v2.reviews   import api as reviews_ns
    from app.api.v2.amenities import api as amenities_ns
    from app.api.v2.bookings  import api as bookings_ns

    api.add_namespace(auth_ns,      path='/auth')
    api.add_namespace(users_ns,     path='/users')
    api.add_namespace(places_ns,    path='/places')
    api.add_namespace(reviews_ns,   path='/reviews')
    api.add_namespace(amenities_ns, path='/amenities')
    api.add_namespace(bookings_ns,  path='/bookings')

    # ── Create tables ─────────────────────────────────────────────────────
    with app.app_context():
        from app.models import user, place, review, amenity, booking  # noqa
        db.create_all()

    return app