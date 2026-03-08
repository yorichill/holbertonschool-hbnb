from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('bookings', description='Booking / reservation operations')

booking_model = api.model('Booking', {
    'place_id': fields.String(required=True, description='ID of the place to book'),
    'user_id': fields.String(required=True, description='ID of the user making the booking'),
    'check_in': fields.String(required=True, description='Check-in date (YYYY-MM-DD)'),
    'check_out': fields.String(required=True, description='Check-out date (YYYY-MM-DD)'),
    'guests': fields.Integer(default=1, description='Number of guests'),
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

    @api.expect(booking_model, validate=True)
    @api.response(201, 'Booking created successfully')
    @api.response(400, 'Validation error')
    @api.response(404, 'Place or user not found')
    @api.response(409, 'Dates conflict with an existing booking')
    def post(self):
        """Create a new booking for a place"""
        data = api.payload

        # Validate foreign keys
        if not facade.get_place(data['place_id']):
            api.abort(404, 'Place not found')
        if not facade.get_user(data['user_id']):
            api.abort(404, 'User not found')

        try:
            booking = facade.create_booking(data)
        except ValueError as e:
            # Conflict vs plain validation
            msg = str(e)
            code = 409 if 'overlap' in msg.lower() or 'conflict' in msg.lower() else 400
            api.abort(code, msg)

        return _enrich(booking), 201

    @api.response(200, 'List of all bookings')
    def get(self):
        """Retrieve all bookings"""
        return [_enrich(b) for b in facade.get_all_bookings()], 200


# ── Single resource ───────────────────────────────────────────────────────────

@api.route('/<string:booking_id>')
class BookingResource(Resource):

    @api.response(200, 'Booking details')
    @api.response(404, 'Booking not found')
    def get(self, booking_id):
        """Get a booking by ID"""
        booking = _get_or_404(booking_id)
        return _enrich(booking), 200

    @api.expect(booking_model)
    @api.response(200, 'Booking updated')
    @api.response(400, 'Validation error')
    @api.response(404, 'Booking not found')
    def put(self, booking_id):
        """Update a booking (dates / guests)"""
        _get_or_404(booking_id)
        try:
            facade.update_booking(booking_id, api.payload)
        except ValueError as e:
            api.abort(400, str(e))
        return _enrich(facade.get_booking(booking_id)), 200

    @api.response(200, 'Booking deleted')
    @api.response(404, 'Booking not found')
    def delete(self, booking_id):
        """Delete a booking"""
        _get_or_404(booking_id)
        facade.delete_booking(booking_id)
        return {'message': 'Booking deleted successfully'}, 200


# ── Status transition ─────────────────────────────────────────────────────────

@api.route('/<string:booking_id>/status')
class BookingStatus(Resource):

    @api.expect(status_model, validate=True)
    @api.response(200, 'Status updated')
    @api.response(400, 'Invalid transition')
    @api.response(404, 'Booking not found')
    def patch(self, booking_id):
        """Confirm or cancel a booking"""
        booking = _get_or_404(booking_id)
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

    @api.response(200, 'Bookings for a user')
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get all bookings made by a specific user"""
        if not facade.get_user(user_id):
            api.abort(404, 'User not found')
        return [_enrich(b) for b in facade.get_bookings_by_user(user_id)], 200


@api.route('/places/<string:place_id>')
class PlaceBookings(Resource):

    @api.response(200, 'Bookings for a place')
    @api.response(404, 'Place not found')
    def get(self, place_id):
        """Get all bookings for a specific place"""
        if not facade.get_place(place_id):
            api.abort(404, 'Place not found')
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
    user = facade.get_user(booking.user_id)
    if place:
        data['place_title'] = place.title
        data['price_per_night'] = place.price
        data['total_price'] = round(place.price * booking.nights, 2)
    if user:
        data['guest_name'] = f"{user.first_name} {user.last_name}"
    return data
