# app/api/v1/amenities.py
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt
from app.services import facade

api = Namespace('amenities', description='Opérations sur les équipements')

amenity_model = api.model('Amenity', {
    'name': fields.String(required=True, description="Le nom de l'équipement")
})


@api.route('/')
class AmenityList(Resource):

    @api.response(200, 'List of amenities')
    def get(self):
        """Lister toutes les amenities (public)"""
        amenities = facade.get_all_amenities()
        return [{'id': a.id, 'name': a.name} for a in amenities], 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(201, 'Amenity created')
    @api.response(400, 'Validation error')
    @api.response(403, 'Admin privileges required')
    def post(self):
        """Créer une amenity (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        try:
            new_amenity = facade.create_amenity(api.payload)
            return {'id': new_amenity.id, 'name': new_amenity.name}, 201
        except ValueError as e:
            return {'error': str(e)}, 400


@api.route('/<string:amenity_id>')
class AmenityResource(Resource):

    @api.response(200, 'Amenity details')
    @api.response(404, 'Amenity not found')
    def get(self, amenity_id):
        """Récupérer une amenity via son ID (public)"""
        amenity = facade.get_amenity(amenity_id)
        if not amenity:
            return {'error': 'Amenity non trouvée'}, 404
        return {'id': amenity.id, 'name': amenity.name}, 200

    @jwt_required()
    @api.expect(amenity_model, validate=True)
    @api.response(200, 'Amenity updated')
    @api.response(403, 'Admin privileges required')
    @api.response(404, 'Amenity not found')
    def put(self, amenity_id):
        """Modifier une amenity (admin uniquement)"""
        claims = get_jwt()
        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403
        try:
            updated = facade.update_amenity(amenity_id, api.payload)
            return {'id': updated.id, 'name': updated.name}, 200
        except ValueError as e:
            return {'error': str(e)}, 400
        except Exception:
            return {'error': 'Amenity non trouvée'}, 404
