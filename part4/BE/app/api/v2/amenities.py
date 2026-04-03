from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade

api = Namespace('amenities', description='Amenity operations')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description='Amenity name'),
})


# ── Collection ────────────────────────────────────────────────────────────────

@api.route('/')
class AmenityList(Resource):

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity created')
    @api.response(400, 'Validation error')
    @api.response(403, 'Admin rights required')
    def post(self):
        """Create a new amenity — admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            api.abort(403, 'Admin rights required')

        try:
            amenity = facade.create_amenity(api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return amenity.to_dict(), 201

    @api.response(200, 'List of amenities')
    def get(self):
        """Retrieve all amenities — public"""
        return [a.to_dict() for a in facade.get_all_amenities()], 200


# ── Single resource ───────────────────────────────────────────────────────────

@api.route('/<string:amenity_id>')
class AmenityResource(Resource):

    @api.response(200, 'Amenity details')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Get an amenity by ID — public"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')
        return amenity.to_dict(), 200

    @jwt_required()
    @api.expect(amenity_model)
    @api.response(200, 'Amenity updated')
    @api.response(400, 'Validation error')
    @api.response(403, 'Admin rights required')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Update an amenity — admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            api.abort(403, 'Admin rights required')

        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            api.abort(404, 'Amenity not found')

        try:
            facade.update_amenity(amenity_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))

        return facade.get_amenity(amenity_id).to_dict(), 200