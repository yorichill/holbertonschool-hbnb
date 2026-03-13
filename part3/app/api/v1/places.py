# app/api/v1/places.py
from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity

api = Namespace('places', description='Oplace operation')

place_model = api.model('Place', {
    'title':       fields.String(required=True, description="Le titre du lieu"),
    'description': fields.String(description="La description du lieu"),
    'price':       fields.Float(required=True, description="Le prix par nuit"),
    'latitude':    fields.Float(required=True, description="La latitude"),
    'longitude':   fields.Float(required=True, description="La longitude"),
    'owner_id':    fields.String(required=True, description="L'ID du propriétaire"),
})


@api.route('/')
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
            
    # Ne touche pas au def get(self): ! Il doit rester public sans @jwt_required


@api.route('/<place_id>')
class PlaceResource(Resource):
    # Ne touche pas au def get(self, place_id): ! Il reste public
    
    @api.expect(place_model)
    @jwt_required() # <-- Le videur
    def put(self, place_id):
        """Update a place's details"""
        current_user = get_jwt_identity()
        place = facade.get_place(place_id)
        
        if not place:
            return {'error': 'Place not found'}, 404
            
        # VÉRIFICATION : Est-ce que le gars connecté est le propriétaire ?
        if place.owner_id != current_user:
            return {'error': 'Unauthorized action'}, 403 # 403 = Interdit !
            
        try:
            facade.update_place(place_id, api.payload)
            return {'message': 'Place updated successfully'}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Lieu non trouvé'}, 404