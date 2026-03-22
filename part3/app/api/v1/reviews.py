from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text':     fields.String(required=True, description='Review text'),
    'rating':   fields.Integer(required=True, description='Rating (1-5)'),
    'place_id': fields.String(required=True, description='Place ID'),
    'user_id':  fields.String(required=True, description='User ID'),
})


@api.route('/')
class ReviewList(Resource):

    @jwt_required()
    @api.expect(review_model, validate=True)
    @api.response(201, 'Review created')
    @api.response(400, 'Validation error')
    @api.response(403, 'Unauthorized action')
    def post(self):
        """Create a new review (authentifié)"""
        current_user_id = get_jwt_identity()
        data = dict(api.payload)
        data['user_id'] = current_user_id  # force l'auteur à l'user connecté

        place = facade.get_place(data['place_id'])
        if not place:
            api.abort(404, 'Place not found')

        # L'owner ne peut pas reviewer son propre lieu
        if place.owner_id == current_user_id:
            return {'error': 'You cannot review your own place'}, 400

        # Un user ne peut reviewer qu'une seule fois par lieu
        existing = facade.get_reviews_by_place(data['place_id'])
        if any(r.user_id == current_user_id for r in existing):
            return {'error': 'You have already reviewed this place'}, 400

        try:
            review = facade.create_review(data)
        except ValueError as e:
            api.abort(400, str(e))
        return review.to_dict(), 201

    @api.response(200, 'List of reviews')
    def get(self):
        """Retrieve all reviews (public)"""
        return [r.to_dict() for r in facade.get_all_reviews()], 200


@api.route('/<string:review_id>')
class ReviewResource(Resource):

    @api.response(200, 'Review details')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get a review by ID (public)"""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')
        return review.to_dict(), 200

    @jwt_required()
    @api.expect(review_model, validate=True)
    @api.response(200, 'Review updated')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """Update a review (auteur ou admin)"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')

        if not is_admin and review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.update_review(review_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return facade.get_review(review_id).to_dict(), 200

    @jwt_required()
    @api.response(200, 'Review deleted')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review (auteur ou admin)"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)

        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')

        if not is_admin and review.user_id != current_user_id:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):

    @api.response(200, 'Reviews for place')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a place (public)"""
        if not facade.get_place(place_id):
            api.abort(404, 'Place not found')
        return [r.to_dict() for r in facade.get_reviews_by_place(place_id)], 200
