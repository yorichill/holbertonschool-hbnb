# app/api/v1/users.py
from flask_restx import Namespace, Resource, fields, abort
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # <-- AJOUT

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name':  fields.String(required=True, description='Nom'),
    'email':      fields.String(required=True, description='Adresse email'),
    'password':   fields.String(required=True, description='Mot de passe'),
})

user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(required=False, description='Prénom'),
    'last_name':  fields.String(required=False, description='Nom'),
    'email':      fields.String(required=False, description='Email (Admin only)'),
    'password':   fields.String(required=False, description='Mot de passe (Admin only)'),
})


@api.route('/')
class UserList(Resource):

    @api.expect(user_model, validate=True)
    @api.response(201, 'User created')
    @api.response(400, 'Validation error / Email already registered')
    @api.response(403, 'Admin privileges required')
    @jwt_required() # 👑 NOUVEAU : Réservé aux connectés (et admins)
    def post(self):
        """Create a new user (Admin only)"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            return {'error': 'Admin privileges required'}, 403 # Blocage des non-admins

        data = api.payload
        email = data.get('email')

        # Vérification si l'email existe déjà
        if hasattr(facade, 'get_user_by_email') and facade.get_user_by_email(email):
            return {'error': 'Email already registered'}, 400

        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except ValueError as e:
            abort(400, message=str(e))

    @api.response(200, 'List of users')
    def get(self):
        """Get all users"""
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
    @jwt_required()
    def put(self, user_id):
        """Update a user by ID"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # 👑 Si pas admin ET ce n'est pas son propre profil : Dehors !
        if not is_admin and current_user != user_id:
            return {'error': 'Unauthorized action'}, 403

        user = facade.user_repo.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        data = api.payload
        
        # 👑 Si pas admin, on bloque la modif d'email et mot de passe
        if not is_admin and ('email' in data or 'password' in data):
            return {'error': 'You cannot modify email or password'}, 400

        # 👑 Si admin, on vérifie que le nouvel email n'est pas déjà pris
        if is_admin and 'email' in data:
            if hasattr(facade, 'get_user_by_email'):
                existing_user = facade.get_user_by_email(data['email'])
                if existing_user and existing_user.id != user_id:
                    return {'error': 'Email already in use'}, 400

        try:
            facade.user_repo.update(user_id, data)
            return facade.user_repo.get(user_id).to_dict(), 200
        except ValueError as e:
            return {'error': str(e)}, 400