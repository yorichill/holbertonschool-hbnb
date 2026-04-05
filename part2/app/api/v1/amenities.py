from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Amenity name'),
})


@api.route('/')
class AmenityList(Resource):
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity created')
    @api.response(400, 'Validation error')
    def post(self):
        """Create a new amenity"""
        try:
            amenity = facade.create_amenity(api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return amenity.to_dict(), 201

    @api.response(200, 'List of amenities')
    def get(self):
        """Retrieve all amenities"""
        return [a.to_dict() for a in facade.get_all_amenities()], 200


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):
    @api.response(200, 'Amenity details')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get an amenity by ID"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        return amenity.to_dict(), 200

    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update an amenity"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        try:
            facade.update_amenity(amenity_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return facade.get_amenity(amenity_id).to_dict(), 200
