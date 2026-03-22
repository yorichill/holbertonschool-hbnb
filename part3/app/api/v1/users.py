from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name':  fields.String(required=True, description='Nom'),
    'email':      fields.String(required=True, description='Adresse email'),
    'password':   fields.String(required=True, description='Mot de passe'),
})

update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='Prénom'),
    'last_name':  fields.String(description='Nom'),
    'email':      fields.String(description='Adresse email (admin seulement)'),
    'password':   fields.String(description='Mot de passe (admin seulement)'),
})


@api.route('/')
class UserList(Resource):

    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Invalid data')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Créer un user (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        if facade.get_user_by_email(api.payload.get('email')):
            return {'error': 'Email already registered'}, 400

        try:
            user = facade.create_user(api.payload)
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

    @jwt_required()
    @api.expect(update_model, validate=True)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Validation error')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update a user"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        # Un user normal ne peut modifier que lui-même
        if not is_admin and current_user_id != user_id:
            return {'error': 'Unauthorized action'}, 403

        user = facade.user_repo.get(user_id)
        if not user:
            return {'error': 'User not found'}, 404

        data = dict(api.payload)  # Convertir le payload en dict pour manipulation

        # Un user normal ne peut pas modifier son email ou mot de passe
        if not is_admin:
            if 'email' in data or 'password' in data:
                return {'error': 'You cannot modify email or password'}, 400
        else:
            # Admin : vérifier que l'email n'est pas déjà utilisé par un autre user
            if 'email' in data:
                existing_user = facade.get_user_by_email(data['email'])
                if existing_user and existing_user.id != user_id:
                    return {'error': 'Email already registered'}, 400

        try:
            return facade.update_user(user_id, data).to_dict(), 200
        except ValueError as e:
            abort(400, message=str(e))
