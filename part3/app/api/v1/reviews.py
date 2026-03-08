# app/api/v1/reviews.py
from flask_restx import Namespace, Resource, fields
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

    @api.expect(review_model, validate=True)
    @api.response(201, 'Review created')
    @api.response(400, 'Validation error')
    def post(self):
        """Create a new review"""
        data = api.payload
        if not facade.get_place(data['place_id']):
            api.abort(404, 'Place not found')
        if not facade.get_user(data['user_id']):
            api.abort(404, 'User not found')
        try:
            review = facade.create_review(data)
        except ValueError as e:
            api.abort(400, str(e))
        return review.to_dict(), 201

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
            api.abort(404, 'Review not found')
        return review.to_dict(), 200

    @api.expect(review_model, validate=True)  # ✅ AJOUT validate=True — manquait
    @api.response(200, 'Review updated')
    @api.response(400, 'Validation error')
    @api.response(404, 'Review not found')
    def put(self, review_id):
        """Update a review"""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')
        try:
            facade.update_review(review_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return facade.get_review(review_id).to_dict(), 200

    @api.response(200, 'Review deleted')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, 'Review not found')
        facade.delete_review(review_id)
        return {'message': 'Review deleted successfully'}, 200


@api.route('/places/<string:place_id>/reviews')
class PlaceReviewList(Resource):

    @api.response(200, 'Reviews for place')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a place"""
        if not facade.get_place(place_id):
            api.abort(404, 'Place not found')
        return [r.to_dict() for r in facade.get_reviews_by_place(place_id)], 200