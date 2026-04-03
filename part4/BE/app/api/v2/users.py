from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('users', description='User operations')

user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name'),
    'last_name':  fields.String(required=True, description='Last name'),
    'email':      fields.String(required=True, description='Email address'),
    'password':   fields.String(required=True, description='Password'),
})

admin_model = api.model('AdminPromotion', {
    'is_admin': fields.Boolean(required=True, description='Grant or revoke admin rights'),
})


# ── Collection ────────────────────────────────────────────────────────────────

@api.route('/')
class UserList(Resource):

    @api.expect(user_model, validate=True)
    @api.response(201, 'User created successfully')
    @api.response(400, 'Validation error')
    def post(self):
        """Register a new user — public"""
        data = api.payload
        if facade.get_user_by_email(data['email']):
            api.abort(400, 'Email already registered')
        try:
            user = facade.create_user(data)
        except ValueError as e:
            api.abort(400, str(e))
        return {'id': user.id, 'message': 'User created successfully'}, 201

    @api.response(200, 'List of users retrieved')
    def get(self):
        """Retrieve all users — public"""
        return [u.to_dict() for u in facade.get_all_users()], 200


# ── Single resource ───────────────────────────────────────────────────────────

@api.route('/<string:user_id>')
class UserResource(Resource):

    @api.response(200, 'User details retrieved')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get a user by ID — public"""
        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')
        return user.to_dict(), 200

    @jwt_required()
    @api.expect(user_model)
    @api.response(200, 'User updated successfully')
    @api.response(400, 'Validation error')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update a user — soi-même ou admin"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')

        if current_user_id != user_id and not is_admin:
            api.abort(403, 'Unauthorized action')

        data = dict(api.payload)

        # ── Champs toujours interdits via ce endpoint ──────────────────────
        # is_admin ne se modifie QUE via PATCH /<id>/admin (endpoint dédié)
        for forbidden in ('is_admin',):
            if forbidden in data:
                api.abort(400, f"Cannot modify '{forbidden}' via this endpoint")

        # Les non-admins ne peuvent pas changer email ni password
        if not is_admin:
            for restricted in ('email', 'password'):
                if restricted in data:
                    api.abort(400, f"You cannot modify '{restricted}'")

        try:
            facade.update_user(user_id, data)
        except ValueError as e:
            api.abort(400, str(e))

        return facade.get_user(user_id).to_dict(), 200


# ── Admin promotion ───────────────────────────────────────────────────────────

@api.route('/<string:user_id>/admin')
class UserAdminPromotion(Resource):

    @jwt_required()
    @api.expect(admin_model, validate=True)
    @api.response(200, 'Admin status updated')
    @api.response(403, 'Admin rights required')
    @api.response(404, 'User not found')
    def patch(self, user_id):
        """Grant or revoke admin rights — admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            api.abort(403, 'Admin rights required')

        user = facade.get_user(user_id)
        if not user:
            api.abort(404, 'User not found')

        new_value = api.payload['is_admin']
        facade.update_user(user_id, {'is_admin': new_value})

        action = 'granted' if new_value else 'revoked'
        return {
            'message': f"Admin rights {action} for user {user_id}",
            'user': facade.get_user(user_id).to_dict()
        }, 200
        