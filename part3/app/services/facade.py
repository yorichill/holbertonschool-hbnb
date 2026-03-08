from app.persistence.repository import InMemoryRepository
from app.models.user import User
from app.models.place import Place
from app.models.amenity import Amenity
from app.models.review import Review
from app.models.booking import Booking

class HBnBFacade:
    def __init__(self):
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.booking_repo = InMemoryRepository()


     # ── User ──────────────────────────────────────────────────────────────────

    def create_user(self, user_data: dict):
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id: str):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email: str):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id: str, data: dict):
        self.user_repo.update(user_id, data)

    # méthode amentity

    def create_amenity(self, amenity_data):
        amenity = Amenity(name=amenity_data['name'])
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        self.amenity_repo.update(amenity_id, amenity_data)
        return self.get_amenity(amenity_id)

    # méthode place

    def create_place(self, place_data):
        owner_id = place_data.get('owner_id')
        owner = self.user_repo.get(owner_id)

        if not owner:
            raise ValueError("Le propriétaire spécifié n'existe pas.")

        place = Place(
            name=place_data.get('name', place_data['title']),
            title=place_data['title'],
            description=place_data.get('description', ''),
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner_id=owner_id
        )

        self.place_repo.add(place)
        return place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        self.place_repo.update(place_id, place_data)
        return self.get_place(place_id)

    # ── Review ────────────────────────────────────────────────────────────────

    def create_review(self, review_data: dict):
        review = Review(**review_data)
        self.review_repo.add(review)
        return review

    def get_review(self, review_id: str):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id: str):
        return [r for r in self.review_repo.get_all() if r.place_id == place_id]

    def update_review(self, review_id: str, data: dict):
        self.review_repo.update(review_id, data)

    def delete_review(self, review_id: str):
        self.review_repo.delete(review_id)

    # ── Booking ───────────────────────────────────────────────────────────────

    def create_booking(self, booking_data: dict):
        booking = Booking(**booking_data)
        self._check_overlap(booking)
        self.booking_repo.add(booking)
        return booking

    def get_booking(self, booking_id: str):
        return self.booking_repo.get(booking_id)

    def get_all_bookings(self, **filters):
        """
        Optional filters for future use, e.g.:
            get_all_bookings(status='confirmed')
        """
        bookings = self.booking_repo.get_all()
        if filters.get('status'):
            bookings = [b for b in bookings if b.status == filters['status']]
        return bookings

    def get_bookings_by_user(self, user_id: str):
        return [b for b in self.booking_repo.get_all() if b.user_id == user_id]

    def get_bookings_by_place(self, place_id: str):
        return [b for b in self.booking_repo.get_all() if b.place_id == place_id]

    def update_booking(self, booking_id: str, data: dict):
        from app.models.booking import Booking
        booking = self.get_booking(booking_id)
        if not booking:
            return

        # Merge incoming data with existing values, then re-validate via a
        # temporary Booking instance (reuses all model validation for free)
        merged = {
            'place_id':  booking.place_id,
            'user_id':   booking.user_id,
            'check_in':  data.get('check_in',  booking.check_in.isoformat()),
            'check_out': data.get('check_out', booking.check_out.isoformat()),
            'guests':    data.get('guests',    booking.guests),
        }
        tmp = Booking(**merged)
        self._check_overlap(tmp, exclude_id=booking_id)

        booking.check_in  = tmp.check_in
        booking.check_out = tmp.check_out
        booking.guests    = tmp.guests

        from datetime import datetime
        booking.updated_at = datetime.utcnow()

    def delete_booking(self, booking_id: str):
        self.booking_repo.delete(booking_id)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _check_overlap(self, new_booking, exclude_id: str = None):
        """Raise ValueError if new_booking overlaps any active booking for the same place."""
        for b in self.booking_repo.get_all():
            if b.id == exclude_id:
                continue
            if b.place_id != new_booking.place_id:
                continue
            if b.status == 'cancelled':
                continue
            if new_booking.check_in < b.check_out and new_booking.check_out > b.check_in:
                raise ValueError(
                    f"Dates conflict with an existing booking "
                    f"({b.check_in} → {b.check_out})."
                )
