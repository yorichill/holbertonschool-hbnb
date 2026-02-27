from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('amenities', description='Opérations sur les équipements')

# Modèle pour valider les données envoyées par l'utilisateur
amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description="Le nom de l'équipement")
})

@api.route('/')
class AmenityList(Resource):
    def get(self):
        """Lister toutes les amenities"""
        amenities = facade.get_all_amenities()
        return [{'id': a.id, 'name': a.name} for a in amenities], 200

    @api.expect(amenity_model)
    def post(self):
        """Créer une amenity"""
        try:
            new_amenity = facade.create_amenity(api.payload)
            return {'id': new_amenity.id, 'name': new_amenity.name}, 201
        except ValueError as e:
            return {'error': str(e)}, 400 # Gère l'erreur 400 demandée

@api.route('/<amenity_id>')
class AmenityResource(Resource):
    def get(self, amenity_id):
        """Récupérer une amenity via son ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity non trouvée'}, 404 # Gère l'erreur 404 demandée
        return {'id': amenity.id, 'name': amenity.name}, 200

    @api.expect(amenity_model)
    def put(self, amenity_id):
        """Modifier une amenity"""
        try:
            updated = facade.update_amenity(amenity_id, api.payload)
            return {'id': updated.id, 'name': updated.name}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Amenity non trouvée'}, 404