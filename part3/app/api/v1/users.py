# app/api/v1/users.py
from flask_restx import Namespace, Resource, fields, abort
from app.services import facade
from app import bcrypt

api = Namespace('users', description='User operations')

# ✅ AJOUT du modèle — manquait complètement
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='Prénom'),
    'last_name':  fields.String(required=True, description='Nom'),
    'email':      fields.String(required=True, description='Adresse email'),
    'password':   fields.String(required=True, description='Mot de passe'),
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)  # ✅ AJOUT — manquait
    @api.response(201, 'User created')
    @api.response(400, 'Validation error')
    def post(self):
        """Create a new user"""
        try:
            user = facade.create_user(api.payload)  # ✅ api.payload et non request.get_json()
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

    @api.expect(user_model, validate=True)  # ✅ AJOUT — manquait
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Validation error')
    @api.response(401, 'Invalid or missing token')
    @api.response(403, 'Unauthorized access')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update a user by ID"""
        user = facade.user_repo.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        try:
            facade.user_repo.update(user_id, api.payload)  # ✅ api.payload
            return facade.user_repo.get(user_id).to_dict(), 200
        except ValueError as e:
            abort(400, message=str(e))
