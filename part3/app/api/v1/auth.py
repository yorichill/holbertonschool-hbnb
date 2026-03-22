from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token
from app.services import facade

api = Namespace('auth', description='Authentication operations')

# Modèle pour vérifier que l'utilisateur envoie bien un email et un mot de passe
login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authentifie l'utilisateur et renvoie un token JWT"""
        credentials = api.payload

        # Étape 1 : On cherche l'utilisateur via son email
        user = facade.get_user_by_email(credentials['email'])

        # Étape 2 : On vérifie s'il existe ET si le mot de passe correspond au hash
        if not user or not user.verify_password(credentials['password']):
            return {'error': 'Invalid credentials'}, 401

        # Étape 3 : On crée le fameux bracelet VIP (Token JWT)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={"is_admin": user.is_admin}
        )

        # Étape 4 : On le donne à l'utilisateur
        return {'access_token': access_token}, 200

# N'oublie pas d'ajouter ces imports tout en haut de ton fichier auth.py s'ils n'y sont pas déjà :
from flask_jwt_extended import jwt_required, get_jwt_identity

# ... (ton code de la classe Login) ...

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required() # <-- C'est ici que le videur se place !
    def get(self):
        """Un endpoint protégé qui nécessite un token JWT valide"""
        # On lit le token pour savoir qui est le porteur du bracelet
        current_user = get_jwt_identity()

        return {'message': f'Hello, user {current_user}'}, 200
