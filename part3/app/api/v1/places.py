# app/api/v1/places.py
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Opérations sur les lieux (Places)')

place_model = api.model('Place', {
    'title':       fields.String(required=True, description="Le titre du lieu"),
    'description': fields.String(description="La description du lieu"),
    'price':       fields.Float(required=True, description="Le prix par nuit"),
    'latitude':    fields.Float(required=True, description="La latitude"),
    'longitude':   fields.Float(required=True, description="La longitude"),
    'owner_id':    fields.String(required=True, description="L'ID du propriétaire"),
})


@api.route('/')
class PlaceList(Resource):

    @api.response(200, 'List of places')
    def get(self):
        """Lister tous les lieux"""
        places = facade.get_all_places()
        return [
            {'id': p.id, 'title': p.title,
             'latitude': p.latitude, 'longitude': p.longitude}
            for p in places
        ], 200

    @api.expect(place_model, validate=True)  # ✅ AJOUT validate=True — manquait
    @api.response(201, 'Place created')
    @api.response(400, 'Validation error')
    def post(self):
        """Créer un nouveau lieu"""
        try:
            new_place = facade.create_place(api.payload)
            return {
                'id':       new_place.id,
                'title':    new_place.title,
                'price':    new_place.price,
                'owner_id': new_place.owner_id,
            }, 201
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/<string:place_id>')
class PlaceResource(Resource):

    @api.response(200, 'Place details')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Récupérer un lieu via son ID"""
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Lieu non trouvé'}, 404
        owner = facade.get_user(place.owner_id)
        return {
            'id':          place.id,
            'title':       place.title,
            'description': place.description,
            'price':       place.price,
            'latitude':    place.latitude,
            'longitude':   place.longitude,
            'owner': {
                'id':         owner.id,
                'first_name': owner.first_name,
                'last_name':  owner.last_name,
            } if owner else None,
            'amenities': place.amenities,
        }, 200

    @api.expect(place_model, validate=True)  # ✅ AJOUT validate=True — manquait
    @api.response(200, 'Place updated')
    @api.response(400, 'Validation error')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        """Modifier un lieu"""
        try:
            updated = facade.update_place(place_id, api.payload)
            return {'id': updated.id, 'title': updated.title}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Lieu non trouvé'}, 404