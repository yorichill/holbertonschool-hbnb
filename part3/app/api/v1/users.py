# app/api/v1/users.py
from flask_restx import Namespace, Resource, fields, abort
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('users', description='User operations')

# Modèle complet pour la création (POST)
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name':  fields.String(required=True, description='Nom'),
    'email':      fields.String(required=True, description='Adresse email'),
    'password':   fields.String(required=True, description='Mot de passe'),
})

# Modèle allégé pour la modification (PUT) pour que Swagger ne force pas l'email/password
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False, description='Prénom'),
    'last_name':  fields.String(required=False, description='Nom'),
})


@api.route('/')
class UserList(Resource):

    @api.expect(user_model, validate=True)
    @api.response(201, 'User created')
    @api.response(400, 'Validation error')
    def post(self):
        """Create a new user"""
        try:
            user = facade.create_user(api.payload)
            return user.to_dict(), 201
        except ValueError as e:
            abort(400, message=str(e))

    @api.response(200, 'List of users')
    def get(self):
        """Get all users"""
        # Note : On garde cette route publique pour que n'importe qui puisse voir les profils
        return [u.to_dict() for u in facade.user_repo.get_all()], 200


@api.route('/<string:user_id>')
class UserDetail(Resource):

    @api.response(200, 'User details')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get a user by ID"""
        user = facade.user_repo.get(user_id)
        if not user:
            abort(404, message='User not found')
        return user.to_dict(), 200

    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User updated')
    @api.response(400, 'Validation error or restricted fields modification')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    @jwt_required() # <-- Le videur est là !
    def put(self, user_id):
        """Update a user by ID"""
        current_user = get_jwt_identity()

        # RÈGLE 1 : On vérifie que l'utilisateur modifie bien SON profil
        if current_user != user_id:
            return {'error': 'Unauthorized action'}, 403

        user = facade.user_repo.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        data = api.payload
        
        # RÈGLE 2 : On bloque toute tentative de modification de l'email ou du mot de passe
        if 'email' in data or 'password' in data:
            return {'error': 'You cannot modify email or password'}, 400

        try:
            facade.user_repo.update(user_id, data)
            return facade.user_repo.get(user_id).to_dict(), 200
        except ValueError as e:
            return {'error': str(e)}, 400