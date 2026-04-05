from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name': fields.String(required=True, description='Last name'),
    'email': fields.String(required=True, description='Email address'),
})


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User created successfully')
    @api.response(400, 'Validation error')
    def post(self):
        """Register a new user"""
        data = api.payload
        # Check for duplicate email
        if facade.get_user_by_email(data['email']):
            api.abort(400, 'Email already registered')
        try:
            user = facade.create_user(data)
        except ValueError as e:
            api.abort(400, str(e))
        return user.to_dict(), 201

    @api.response(200, 'List of users retrieved')
    def get(self):
        """Retrieve all users"""
        return [u.to_dict() for u in facade.get_all_users()], 200


@api.route('/<string:user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get a user by ID"""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user.to_dict(), 200

    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(404, 'User not found')
    @api.response(400, 'Validation error')
    def put(self, user_id):
        """Update a user"""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        try:
            facade.update_user(user_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return facade.get_user(user_id).to_dict(), 200
