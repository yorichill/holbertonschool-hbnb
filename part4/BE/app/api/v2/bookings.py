from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('bookings', description='Booking / reservation operations')

booking_model = api.model('Booking', {
    'place_id':  fields.String(required=True, description='ID of the place to book'),
    'user_id':   fields.String(required=True, description='ID of the user making the booking'),
    'check_in':  fields.String(required=True, description='Check-in date (YYYY-MM-DD)'),
    'check_out': fields.String(required=True, description='Check-out date (YYYY-MM-DD)'),
    'guests':    fields.Integer(default=1, description='Number of guests'),
})

status_model = api.model('BookingStatus', {
    'status': fields.String(
        required=True,
        description='New status: confirmed | cancelled',
        enum=['confirmed', 'cancelled']
    ),
})


# ── Collection ────────────────────────────────────────────────────────────────

@api.route('/')
class BookingList(Resource):

    @jwt_required()
    @api.expect(booking_model, validate=True)
    @api.response(201, 'Booking created successfully')
    @api.response(400, 'Validation error')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place or user not found')
    @api.response(409, 'Dates conflict with an existing booking')
    def post(self):
        """Create a new booking — authentifié requis"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        data = api.payload

        # Un user ne peut créer une réservation qu'en son propre nom
        # (un admin peut réserver pour n'importe qui)
        if data.get('user_id') != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'You can only create bookings for yourself')

        if not facade.get_place(data['place_id']):
            api.abort(404, 'Place not found')
        if not facade.get_user(data['user_id']):
            api.abort(404, 'User not found')

        try:
            booking = facade.create_booking(data)
        except ValueError as e:
            msg = str(e)
            code = 409 if 'overlap' in msg.lower() or 'conflict' in msg.lower() else 400
            api.abort(code, msg)

        return _enrich(booking), 201

    @jwt_required()
    @api.response(200, 'List of all bookings')
    @api.response(403, 'Admin rights required')
    def get(self):
        """Retrieve all bookings — admin only"""
        claims = get_jwt()
        if not claims.get('is_admin', False):
            api.abort(403, 'Admin rights required')
        return [_enrich(b) for b in facade.get_all_bookings()], 200


# ── Single resource ───────────────────────────────────────────────────────────

@api.route('/<string:booking_id>')
class BookingResource(Resource):

    @jwt_required()
    @api.response(200, 'Booking details')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Booking not found')
    def get(self, booking_id):
        """Get a booking by ID — propriétaire ou admin"""
        booking = _get_or_404(booking_id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user_id != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'Unauthorized action')
        return _enrich(booking), 200

    @jwt_required()
    @api.expect(booking_model)
    @api.response(200, 'Booking updated')
    @api.response(400, 'Validation error')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Booking not found')
    def put(self, booking_id):
        """Update a booking — propriétaire ou admin"""
        booking = _get_or_404(booking_id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user_id != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'Unauthorized action')
        try:
            facade.update_booking(booking_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return _enrich(facade.get_booking(booking_id)), 200

    @jwt_required()
    @api.response(200, 'Booking deleted')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Booking not found')
    def delete(self, booking_id):
        """Delete a booking — propriétaire ou admin"""
        booking = _get_or_404(booking_id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user_id != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'Unauthorized action')
        facade.delete_booking(booking_id)
        return {'message': 'Booking deleted successfully'}, 200


# ── Status transition ─────────────────────────────────────────────────────────

@api.route('/<string:booking_id>/status')
class BookingStatus(Resource):

    @jwt_required()
    @api.expect(status_model, validate=True)
    @api.response(200, 'Status updated')
    @api.response(400, 'Invalid transition')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Booking not found')
    def patch(self, booking_id):
        """Confirm or cancel a booking — propriétaire ou admin"""
        booking = _get_or_404(booking_id)
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if booking.user_id != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'Unauthorized action')

        new_status = api.payload['status']
        try:
            if new_status == 'confirmed':
                booking.confirm()
            elif new_status == 'cancelled':
                booking.cancel()
            else:
                api.abort(400, f"Unknown status: {new_status}")
        except ValueError as e:
            api.abort(400, str(e))
        return _enrich(booking), 200


# ── Filtered views ────────────────────────────────────────────────────────────

@api.route('/users/<string:user_id>')
class UserBookings(Resource):

    @jwt_required()
    @api.response(200, 'Bookings for a user')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get all bookings for a user — soi-même ou admin"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if user_id != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'Unauthorized action')
        if not facade.get_user(user_id):
            api.abort(404, 'User not found')
        return [_enrich(b) for b in facade.get_bookings_by_user(user_id)], 200


@api.route('/places/<string:place_id>')
class PlaceBookings(Resource):

    @jwt_required()
    @api.response(200, 'Bookings for a place')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all bookings for a place — propriétaire de la place ou admin"""
        place = facade.get_place(place_id)
        if not place:
            api.abort(404, 'Place not found')
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        if place.owner_id != current_user_id and not claims.get('is_admin', False):
            api.abort(403, 'Unauthorized action')
        return [_enrich(b) for b in facade.get_bookings_by_place(place_id)], 200


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_or_404(booking_id):
    booking = facade.get_booking(booking_id)
    if not booking:
        api.abort(404, 'Booking not found')
    return booking


def _enrich(booking):
    """Add place title and user name to the serialised booking."""
    data = booking.to_dict()
    place = facade.get_place(booking.place_id)
    user  = facade.get_user(booking.user_id)
    if place:
        data['place_title']    = place.title
        data['price_per_night'] = place.price
        data['total_price']    = round(place.price * booking.nights, 2)
    if user:
        data['guest_name'] = f"{user.first_name} {user.last_name}"
    return data
