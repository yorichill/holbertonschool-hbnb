# app/api/v1/reviews.py
from flask_restx import Namespace, Resource, fields
from app.services import facade
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # <-- AJOUT de get_jwt

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text':     fields.String(required=True, description='Review text'),
    'rating':   fields.Integer(required=True, description='Rating (1-5)'),
    'place_id': fields.String(required=True, description='Place ID'),
    'user_id':  fields.String(required=False, description='User ID (auto-filled via JWT)'),
})


@api.route('/')
class ReviewList(Resource):

    @api.expect(review_model, validate=True)
    @api.response(201, 'Review created')
    @api.response(400, 'Validation error / Rule violation')
    @api.response(404, 'Place not found')
    @jwt_required()
    def post(self):
        """Create a new review"""
        current_user = get_jwt_identity()
        data = api.payload
        place_id = data.get('place_id')

        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        if place.owner_id == current_user:
            return {'error': 'You cannot review your own place.'}, 400

        existing_reviews = facade.get_reviews_by_place(place_id)
        for review in existing_reviews:
            if review.user_id == current_user:
                return {'error': 'You have already reviewed this place.'}, 400

        data['user_id'] = current_user

        try:
            review = facade.create_review(data)
            return review.to_dict(), 201
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'List of reviews')
    def get(self):
        """Retrieve all reviews"""
        return [r.to_dict() for r in facade.get_all_reviews()], 200


@api.route('/<string:review_id>')
class ReviewResource(Resource):

    @api.response(200, 'Review details')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get a review by ID"""
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
        return review.to_dict(), 200

    @api.expect(review_model, validate=True)
    @api.response(200, 'Review updated')
    @api.response(400, 'Validation error')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    def put(self, review_id):
        """Update a review"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False) # 👑 Lecture du rôle Admin

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        # 👑 PASSE-MURAILLE : Autorisé si tu es Admin OU si tu es l'auteur
        if not is_admin and review.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        try:
            facade.update_review(review_id, api.payload)
            updated_review = facade.get_review(review_id)
            return updated_review.to_dict(), 200
        except ValueError as e:
            return {'error': str(e)}, 400

    @api.response(200, 'Review deleted')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Review not found')
    @jwt_required()
    def delete(self, review_id):
        """Delete a review"""
        current_user = get_jwt_identity()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False) # 👑 Lecture du rôle Admin

        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404

        # 👑 PASSE-MURAILLE : Autorisé si tu es Admin OU si tu es l'auteur
        if not is_admin and review.user_id != current_user:
            return {'error': 'Unauthorized action'}, 403

        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200