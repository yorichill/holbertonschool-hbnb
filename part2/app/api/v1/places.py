from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('places', description='Place operations')

place_model = api.model('Place', {
    'title': fields.String(required=True, description='Place title'),
    'description': fields.String(description='Place description'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude'),
    'longitude': fields.Float(required=True, description='Longitude'),
    'owner_id': fields.String(required=True, description='Owner user ID'),
    'amenity_ids': fields.List(fields.String, description='List of amenity IDs'),
})


@api.route('/')
class PlaceList(Resource):
    @api.expect(place_model, validate=True)
    @api.response(201, 'Place created')
    @api.response(400, 'Validation error')
    def post(self):
        """Create a new place"""
        try:
            place = facade.create_place(api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        owner = facade.get_user(place.owner_id)
        return place.to_dict(include_owner=True, owner=owner), 201

    @api.response(200, 'List of places')
    def get(self):
        """Retrieve all places"""
        places = facade.get_all_places()
        result = []
        for place in places:
            owner = facade.get_user(place.owner_id)
            result.append(place.to_dict(include_owner=True, owner=owner))
        return result, 200


@api.route('/<string:place_id>')
class PlaceResource(Resource):
    @api.response(200, 'Place details')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get a place by ID"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        owner = facade.get_user(place.owner_id)
        return place.to_dict(include_owner=True, owner=owner), 200

    @api.expect(place_model)
    @api.response(200, 'Place updated')
    @api.response(404, 'Place not found')
    def put(self, place_id):
        """Update a place"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        try:
            facade.update_place(place_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        updated = facade.get_place(place_id)
        owner = facade.get_user(updated.owner_id)
        return updated.to_dict(include_owner=True, owner=owner), 200
