from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email':    fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload

        user = facade.get_user_by_email(credentials['email'])

        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )

        return {'access_token': access_token}, 200


@api.route('/protected')
class ProtectedResource(Resource):
    from flask_jwt_extended import jwt_required, get_jwt_identity

    @jwt_required()
    def get(self):
        """A protected endpoint to test JWT"""
        from flask_jwt_extended import get_jwt_identity, get_jwt
        current_user = get_jwt_identity()
        claims = get_jwt()
        return {
            'message': f'Hello, user {current_user}',
            'is_admin': claims.get('is_admin', False)
        }, 200