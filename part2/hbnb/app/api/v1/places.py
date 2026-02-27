from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Opérations sur les lieux (Places)')

# POST
place_model = api.model('Place', {
    'title': fields.String(required=True, description="Le titre du lieu"),
    'description': fields.String(description="La description du lieu"),
    'price': fields.Float(required=True, description="Le prix par nuit"),
    'latitude': fields.Float(required=True, description="La latitude"),
    'longitude': fields.Float(required=True, description="La longitude"),
    'owner_id': fields.String(required=True, description="L'ID du propriétaire")
})

@api.route('/')
class PlaceList(Resource):
    def get(self):
        """Lister tous les lieux"""
        places = facade.get_all_places()
        return [{'id': p.id, 'title': p.title, 'latitude': p.latitude, 'longitude': p.longitude} for p in places], 200

    @api.expect(place_model)
    def post(self):
        """Créer un nouveau lieu"""
        try:
            new_place = facade.create_place(api.payload)
            return {
                'id': new_place.id, 
                'title': new_place.title, 
                'price': new_place.price,
                'owner_id': new_place.owner.id
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400 # Gère l'erreur 400

@api.route('/<place_id>')
class PlaceResource(Resource):
    def get(self, place_id):
        """Récupérer un lieu via son ID (avec propriétaire et équipements)"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Lieu non trouvé'}, 404 # Gère l'erreur 404
        
        return {
            'id': place.id,
            'title': place.title,
            'description': place.description,
            'price': place.price,
            'latitude': place.latitude,
            'longitude': place.longitude,
            'owner': {
                'id': place.owner.id,
                'first_name': place.owner.first_name,
                'last_name': place.owner.last_name
            },
            'amenities': [{'id': a.id, 'name': a.name} for a in place.amenities]
        }, 200

    @api.expect(place_model)
    def put(self, place_id):
        """Modifier un lieu"""
        try:
            updated = facade.update_place(place_id, api.payload)
            return {'id': updated.id, 'title': updated.title}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Lieu non trouvé'}, 404