from part4.BE.app.persistence.repository import SQLAlchemyRepository
from part4.BE.app.services.repositories.user_repository import UserRepository


class HBnBFacade:
    def __init__(self):
        from part4.BE.app.models.place import Place
        from part4.BE.app.models.review import Review
        from part4.BE.app.models.amenity import Amenity
        from part4.BE.app.models.booking import Booking

        self.user_repo    = UserRepository()
        self.place_repo   = SQLAlchemyRepository(Place)
        self.review_repo  = SQLAlchemyRepository(Review)
        self.amenity_repo = SQLAlchemyRepository(Amenity)
        self.booking_repo = SQLAlchemyRepository(Booking)

    # ── User ──────────────────────────────────────────────────────────────────

    def create_user(self, user_data: dict):
        from part4.BE.app.models.user import User
        password = user_data.pop('password', None)
        user = User(**user_data)
        if password:
            user.hash_password(password)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id: str):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email: str):
        return self.user_repo.get_user_by_email(email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id: str, data: dict):
        """
        Met à jour un utilisateur.
        - Le mot de passe est re-hashé si fourni.
        - is_admin ne peut être modifié QUE si la clé est explicitement
          présente dans data (réservé à l'endpoint admin PATCH /<id>/admin).
          Depuis users.py PUT, la clé est bloquée avant d'arriver ici.
        """
        user = self.user_repo.get(user_id)
        if not user:
            return

        # Hash du mot de passe si fourni
        if 'password' in data:
            password = data.pop('password')
            user.hash_password(password)

        # Mise à jour des champs autorisés
        SAFE_FIELDS = {'first_name', 'last_name', 'email', 'is_admin'}
        for key, value in data.items():
            if key in SAFE_FIELDS and hasattr(user, key):
                setattr(user, key, value)

        from datetime import datetime
        user.updated_at = datetime.utcnow()

        from part4.BE.app import db
        db.session.commit()

    # ── Amenity ───────────────────────────────────────────────────────────────

    def create_amenity(self, amenity_data: dict):
        from part4.BE.app.models.amenity import Amenity
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id: str):
        return self.amenity_repo.get(amenity_id)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id: str, data: dict):
        self.amenity_repo.update(amenity_id, data)

    # ── Place ─────────────────────────────────────────────────────────────────

    def create_place(self, place_data: dict):
        from part4.BE.app.models.place import Place

        if not self.get_user(place_data.get('owner_id', '')):
            raise ValueError('Owner not found.')

        amenity_ids = place_data.pop('amenity_ids', [])
        place = Place(**place_data)

        for amenity_id in amenity_ids:
            amenity = self.get_amenity(amenity_id)
            if amenity:
                place.amenities.append(amenity)

        self.place_repo.add(place)
        return place

    def get_place(self, place_id: str):
        return self.place_repo.get(place_id)

    def get_all_places(self, **filters):
        places = self.place_repo.get_all()
        if filters.get('min_price') is not None:
            places = [p for p in places if p.price >= filters['min_price']]
        if filters.get('max_price') is not None:
            places = [p for p in places if p.price <= filters['max_price']]
        return places

    def update_place(self, place_id: str, data: dict):
        self.place_repo.update(place_id, data)

    # ── Review ────────────────────────────────────────────────────────────────

    def create_review(self, review_data: dict):
        from part4.BE.app.models.review import Review
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
        from part4.BE.app.models.booking import Booking
        booking = Booking(**booking_data)
        self._check_overlap(booking)
        self.booking_repo.add(booking)
        return booking

    def get_booking(self, booking_id: str):
        return self.booking_repo.get(booking_id)

    def get_all_bookings(self, **filters):
        bookings = self.booking_repo.get_all()
        if filters.get('status'):
            bookings = [b for b in bookings if b.status == filters['status']]
        return bookings

    def get_bookings_by_user(self, user_id: str):
        return [b for b in self.booking_repo.get_all() if b.user_id == user_id]

    def get_bookings_by_place(self, place_id: str):
        return [b for b in self.booking_repo.get_all() if b.place_id == place_id]

    def update_booking(self, booking_id: str, data: dict):
        from part4.BE.app.models.booking import Booking
        booking = self.get_booking(booking_id)
        if not booking:
            return

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

        from part4.BE.app import db
        db.session.commit()

    def delete_booking(self, booking_id: str):
        self.booking_repo.delete(booking_id)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _check_overlap(self, new_booking, exclude_id: str = None):
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
                