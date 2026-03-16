# app/api/v1/places.py
from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

api = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title':       fields.String(required=True, description="Le titre du lieu"),
    'description': fields.String(description="La description du lieu"),
    'price':       fields.Float(required=True, description="Le prix par nuit"),
    'latitude':    fields.Float(required=True, description="La latitude"),
    'longitude':   fields.Float(required=True, description="La longitude"),
    'owner_id':    fields.String(required=False, description="L'ID du propriétaire (auto)"),
})


@api.route('/')
class PlaceList(Resource):
    
    @api.expect(place_model)
    @jwt_required()
    def post(self):
        """Create a new place"""
        current_user = get_jwt_identity() # On lit l'ID dans le token
        place_data = api.payload
        
        # On force l'owner_id à être celui qui est connecté !
        place_data['owner_id'] = current_user 
        
        try:
            new_place = facade.create_place(place_data)
            return {'id': new_place.id, 'title': new_place.title, 'owner_id': new_place.owner_id}, 201
        except ValueError as e:
            return {'error': str(e)}, 400
            
    def get(self):
        """Retrieve all places"""
        return [p.to_dict() for p in facade.get_all_places()], 200


@api.route('/<place_id>')
class PlaceResource(Resource):
    
    def get(self, place_id):
        """Get a place's details"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
        return place.to_dict(), 200
        
    @api.expect(place_model)
    @jwt_required() # <-- Le videur
    def put(self, place_id):
        """Update a place's details"""
        current_user = get_jwt_identity()
        
        # 👑 NOUVEAU : On lit tout le token pour voir si c'est un Admin
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        place = facade.get_place(place_id)
        
        if not place:
            return {'error': 'Place not found'}, 404
            
        # VÉRIFICATION : Si tu n'es PAS admin ET que tu n'es PAS le propriétaire -> Interdit !
        if not is_admin and place.owner_id != current_user:
            return {'error': 'Unauthorized action'}, 403 # 403 = Interdit !
            
        try:
            facade.update_place(place_id, api.payload)
            return {'message': 'Place updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Lieu non trouvé'}, 404