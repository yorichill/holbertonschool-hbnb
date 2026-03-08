"""
test_hbnb_api.py
================
Tests complets pour tous les endpoints de l'API HBnB.
Couvre : Users, Amenities, Places, Reviews, Bookings

Lancement :
    python -m pytest test_hbnb_api.py -v
    # ou
    python -m unittest test_hbnb_api.py
"""

import unittest
from datetime import date, timedelta
from app import create_app


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def today_str():
    return date.today().isoformat()

def future(days: int) -> str:
    return (date.today() + timedelta(days=days)).isoformat()

def past(days: int) -> str:
    return (date.today() - timedelta(days=days)).isoformat()


# ─────────────────────────────────────────────────────────────────────────────
# Base
# ─────────────────────────────────────────────────────────────────────────────

class BaseTestCase(unittest.TestCase):
    """Shared setUp : fresh app + test client for every test."""

    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

    # ── Shortcut helpers ──────────────────────────────────────────────────────

    def _create_user(self, first_name="Arnaud", last_name="Messenet",
                     email="arnaud.messenet@example.com", password="securepass"):
        resp = self.client.post('/api/v1/users/', json={
            "first_name": first_name,
            "last_name":  last_name,
            "email":      email,
            "password":   password,
        })
        return resp

    def _create_amenity(self, name="WiFi"):
        return self.client.post('/api/v1/amenities/', json={"name": name})

    def _create_place(self, owner_id, title="Cozy Flat",
                      price=80.0, latitude=48.8, longitude=2.3):
        return self.client.post('/api/v1/places/', json={
            "title":       title,
            "description": "A nice place",
            "price":       price,
            "latitude":    latitude,
            "longitude":   longitude,
            "owner_id":    owner_id,
        })

    def _create_review(self, place_id, user_id, text="Great!", rating=5):
        return self.client.post('/api/v1/reviews/', json={
            "text":     text,
            "rating":   rating,
            "place_id": place_id,
            "user_id":  user_id,
        })

    def _create_booking(self, place_id, user_id,
                        check_in=None, check_out=None, guests=1):
        check_in  = check_in  or future(5)
        check_out = check_out or future(8)
        return self.client.post('/api/v1/bookings/', json={
            "place_id":  place_id,
            "user_id":   user_id,
            "check_in":  check_in,
            "check_out": check_out,
            "guests":    guests,
        })


# ═════════════════════════════════════════════════════════════════════════════
# 1. USERS
# ═════════════════════════════════════════════════════════════════════════════

class TestUsers(BaseTestCase):

    # ── POST /api/v1/users/ ───────────────────────────────────────────────────

    def test_create_user_success(self):
        resp = self._create_user()
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'Arnaud')
        self.assertEqual(data['email'], 'arnaud.messenet@example.com')

    def test_create_user_missing_fields(self):
        resp = self.client.post('/api/v1/users/', json={})
        self.assertIn(resp.status_code, [400, 422])

    def test_create_user_empty_first_name(self):
        resp = self._create_user(first_name="")
        self.assertIn(resp.status_code, [400, 422])

    def test_create_user_invalid_email(self):
        resp = self._create_user(email="not-an-email")
        self.assertIn(resp.status_code, [400, 422])

    def test_create_user_duplicate_email(self):
        self._create_user(email="valentin.dardenne@example.com")
        resp = self._create_user(email="valentin.dardenne@example.com")
        self.assertIn(resp.status_code, [400, 409])

    # ── GET /api/v1/users/ ────────────────────────────────────────────────────

    def test_list_users(self):
        self._create_user(email="thomas.haenel@example.com")
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_list_users_empty(self):
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    # ── GET /api/v1/users/<id> ────────────────────────────────────────────────

    def test_get_user_by_id(self):
        user_id = self._create_user(email="valentin.dardenne@example.com").get_json()['id']
        resp = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], user_id)

    def test_get_user_not_found(self):
        resp = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── PUT /api/v1/users/<id> ────────────────────────────────────────────────

    def test_update_user(self):
        user_id = self._create_user(email="arnaud.messenet@example.com").get_json()['id']
        resp = self.client.put(f'/api/v1/users/{user_id}', json={
            "first_name": "Thomas",
            "last_name":  "Haenel",
            "email":      "thomas.haenel@example.com",
            "password":   "newpassword",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['first_name'], 'Thomas')

    def test_update_user_not_found(self):
        resp = self.client.put('/api/v1/users/nonexistent-id', json={
            "first_name": "X", "last_name": "Y",
            "email": "x@y.com", "password": "pass1234",
        })
        self.assertEqual(resp.status_code, 404)


# ═════════════════════════════════════════════════════════════════════════════
# 2. AMENITIES
# ═════════════════════════════════════════════════════════════════════════════

class TestAmenities(BaseTestCase):

    # ── POST /api/v1/amenities/ ───────────────────────────────────────────────

    def test_create_amenity_success(self):
        resp = self._create_amenity("Pool")
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Pool')

    def test_create_amenity_missing_name(self):
        resp = self.client.post('/api/v1/amenities/', json={})
        self.assertIn(resp.status_code, [400, 422])

    def test_create_amenity_empty_name(self):
        resp = self.client.post('/api/v1/amenities/', json={"name": ""})
        self.assertIn(resp.status_code, [400, 422])

    # ── GET /api/v1/amenities/ ────────────────────────────────────────────────

    def test_list_amenities(self):
        self._create_amenity("WiFi")
        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    def test_list_amenities_empty(self):
        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    # ── GET /api/v1/amenities/<id> ────────────────────────────────────────────

    def test_get_amenity_by_id(self):
        amenity_id = self._create_amenity("Parking").get_json()['id']
        resp = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'Parking')

    def test_get_amenity_not_found(self):
        resp = self.client.get('/api/v1/amenities/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── PUT /api/v1/amenities/<id> ────────────────────────────────────────────

    def test_update_amenity(self):
        amenity_id = self._create_amenity("Jacuzzi").get_json()['id']
        resp = self.client.put(f'/api/v1/amenities/{amenity_id}',
                               json={"name": "Hot Tub"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'Hot Tub')

    def test_update_amenity_not_found(self):
        resp = self.client.put('/api/v1/amenities/nonexistent-id',
                               json={"name": "X"})
        self.assertEqual(resp.status_code, 404)


# ═════════════════════════════════════════════════════════════════════════════
# 3. PLACES
# ═════════════════════════════════════════════════════════════════════════════

class TestPlaces(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.owner_id = self._create_user(email="arnaud.messenet@example.com").get_json()['id']

    # ── POST /api/v1/places/ ─────────────────────────────────────────────────

    def test_create_place_success(self):
        resp = self._create_place(self.owner_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['owner_id'], self.owner_id)

    def test_create_place_invalid_owner(self):
        resp = self._create_place("nonexistent-owner-id")
        self.assertIn(resp.status_code, [400, 404])

    def test_create_place_negative_price(self):
        resp = self._create_place(self.owner_id, price=-10.0)
        self.assertIn(resp.status_code, [400, 422])

    def test_create_place_zero_price(self):
        resp = self._create_place(self.owner_id, price=0)
        self.assertIn(resp.status_code, [400, 422])

    def test_create_place_invalid_latitude(self):
        resp = self._create_place(self.owner_id, latitude=100.0)
        self.assertIn(resp.status_code, [400, 422])

    def test_create_place_invalid_longitude(self):
        resp = self._create_place(self.owner_id, longitude=200.0)
        self.assertIn(resp.status_code, [400, 422])

    def test_create_place_missing_title(self):
        resp = self.client.post('/api/v1/places/', json={
            "price": 50.0, "latitude": 48.0,
            "longitude": 2.0, "owner_id": self.owner_id,
        })
        self.assertIn(resp.status_code, [400, 422])

    # ── GET /api/v1/places/ ───────────────────────────────────────────────────

    def test_list_places(self):
        self._create_place(self.owner_id)
        resp = self.client.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    # ── GET /api/v1/places/<id> ───────────────────────────────────────────────

    def test_get_place_by_id(self):
        place_id = self._create_place(self.owner_id).get_json()['id']
        resp = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('owner', resp.get_json())

    def test_get_place_not_found(self):
        resp = self.client.get('/api/v1/places/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── PUT /api/v1/places/<id> ───────────────────────────────────────────────

    def test_update_place(self):
        place_id = self._create_place(self.owner_id).get_json()['id']
        resp = self.client.put(f'/api/v1/places/{place_id}', json={
            "title":       "Updated Title",
            "description": "Updated desc",
            "price":       120.0,
            "latitude":    45.0,
            "longitude":   9.0,
            "owner_id":    self.owner_id,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['title'], 'Updated Title')

    def test_update_place_not_found(self):
        resp = self.client.put('/api/v1/places/nonexistent-id', json={
            "title": "X", "price": 10.0,
            "latitude": 0.0, "longitude": 0.0,
            "owner_id": self.owner_id,
        })
        self.assertEqual(resp.status_code, 404)

    # ── Boundary tests ────────────────────────────────────────────────────────

    def test_create_place_boundary_latitude_min(self):
        resp = self._create_place(self.owner_id, latitude=-90.0)
        self.assertEqual(resp.status_code, 201)

    def test_create_place_boundary_latitude_max(self):
        resp = self._create_place(self.owner_id, latitude=90.0)
        self.assertEqual(resp.status_code, 201)

    def test_create_place_boundary_longitude_min(self):
        resp = self._create_place(self.owner_id, longitude=-180.0)
        self.assertEqual(resp.status_code, 201)

    def test_create_place_boundary_longitude_max(self):
        resp = self._create_place(self.owner_id, longitude=180.0)
        self.assertEqual(resp.status_code, 201)


# ═════════════════════════════════════════════════════════════════════════════
# 4. REVIEWS
# ═════════════════════════════════════════════════════════════════════════════

class TestReviews(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user_id  = self._create_user(email="valentin.dardenne@example.com").get_json()['id']
        self.owner_id = self._create_user(email="thomas.haenel@example.com").get_json()['id']
        self.place_id = self._create_place(self.owner_id).get_json()['id']

    # ── POST /api/v1/reviews/ ─────────────────────────────────────────────────

    def test_create_review_success(self):
        resp = self._create_review(self.place_id, self.user_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['rating'], 5)

    def test_create_review_invalid_place(self):
        resp = self._create_review("bad-place-id", self.user_id)
        self.assertIn(resp.status_code, [400, 404])

    def test_create_review_invalid_user(self):
        resp = self._create_review(self.place_id, "bad-user-id")
        self.assertIn(resp.status_code, [400, 404])

    def test_create_review_empty_text(self):
        resp = self.client.post('/api/v1/reviews/', json={
            "text":     "",
            "rating":   3,
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        self.assertIn(resp.status_code, [400, 422])

    def test_create_review_rating_too_high(self):
        resp = self.client.post('/api/v1/reviews/', json={
            "text":     "OK",
            "rating":   6,
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        self.assertIn(resp.status_code, [400, 422])

    def test_create_review_rating_too_low(self):
        resp = self.client.post('/api/v1/reviews/', json={
            "text":     "OK",
            "rating":   0,
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        self.assertIn(resp.status_code, [400, 422])

    def test_create_review_missing_rating(self):
        resp = self.client.post('/api/v1/reviews/', json={
            "text":     "OK",
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        self.assertIn(resp.status_code, [400, 422])

    # ── GET /api/v1/reviews/ ──────────────────────────────────────────────────

    def test_list_reviews(self):
        self._create_review(self.place_id, self.user_id)
        resp = self.client.get('/api/v1/reviews/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    # ── GET /api/v1/reviews/<id> ──────────────────────────────────────────────

    def test_get_review_by_id(self):
        review_id = self._create_review(self.place_id, self.user_id).get_json()['id']
        resp = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], review_id)

    def test_get_review_not_found(self):
        resp = self.client.get('/api/v1/reviews/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── PUT /api/v1/reviews/<id> ──────────────────────────────────────────────

    def test_update_review(self):
        review_id = self._create_review(self.place_id, self.user_id).get_json()['id']
        resp = self.client.put(f'/api/v1/reviews/{review_id}', json={
            "text":     "Updated text",
            "rating":   4,
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['text'], 'Updated text')

    def test_update_review_not_found(self):
        resp = self.client.put('/api/v1/reviews/nonexistent-id', json={
            "text":     "X",
            "rating":   3,
            "place_id": self.place_id,
            "user_id":  self.user_id,
        })
        self.assertEqual(resp.status_code, 404)

    # ── DELETE /api/v1/reviews/<id> ───────────────────────────────────────────

    def test_delete_review(self):
        review_id = self._create_review(self.place_id, self.user_id).get_json()['id']
        resp = self.client.delete(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)
        # Verify it's gone
        self.assertEqual(self.client.get(f'/api/v1/reviews/{review_id}').status_code, 404)

    def test_delete_review_not_found(self):
        resp = self.client.delete('/api/v1/reviews/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── GET /api/v1/reviews/places/<place_id>/reviews ─────────────────────────

    def test_get_reviews_by_place(self):
        self._create_review(self.place_id, self.user_id, text="Nice", rating=4)
        resp = self.client.get(f'/api/v1/reviews/places/{self.place_id}/reviews')
        self.assertEqual(resp.status_code, 200)
        reviews = resp.get_json()
        self.assertTrue(all(r['place_id'] == self.place_id for r in reviews))

    def test_get_reviews_by_invalid_place(self):
        resp = self.client.get('/api/v1/reviews/places/nonexistent-id/reviews')
        self.assertEqual(resp.status_code, 404)


# ═════════════════════════════════════════════════════════════════════════════
# 5. BOOKINGS
# ═════════════════════════════════════════════════════════════════════════════

class TestBookings(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.user_id  = self._create_user(email="valentin.dardenne@example.com").get_json()['id']
        self.owner_id = self._create_user(email="arnaud.messenet@example.com").get_json()['id']
        self.place_id = self._create_place(self.owner_id).get_json()['id']

    # ── POST /api/v1/bookings/ ────────────────────────────────────────────────

    def test_create_booking_success(self):
        resp = self._create_booking(self.place_id, self.user_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['status'], 'pending')
        self.assertIn('total_price', data)

    def test_create_booking_invalid_place(self):
        resp = self._create_booking("bad-place-id", self.user_id)
        self.assertEqual(resp.status_code, 404)

    def test_create_booking_invalid_user(self):
        resp = self._create_booking(self.place_id, "bad-user-id")
        self.assertEqual(resp.status_code, 404)

    def test_create_booking_checkout_before_checkin(self):
        resp = self._create_booking(
            self.place_id, self.user_id,
            check_in=future(10), check_out=future(5)
        )
        self.assertIn(resp.status_code, [400, 422])

    def test_create_booking_same_dates(self):
        d = future(5)
        resp = self._create_booking(
            self.place_id, self.user_id,
            check_in=d, check_out=d
        )
        self.assertIn(resp.status_code, [400, 422])

    def test_create_booking_checkin_in_past(self):
        resp = self._create_booking(
            self.place_id, self.user_id,
            check_in=past(3), check_out=future(2)
        )
        self.assertIn(resp.status_code, [400, 422])

    def test_create_booking_zero_guests(self):
        resp = self._create_booking(self.place_id, self.user_id, guests=0)
        self.assertIn(resp.status_code, [400, 422])

    def test_create_booking_overlap_conflict(self):
        # First booking: days 5-10
        self._create_booking(self.place_id, self.user_id,
                             check_in=future(5), check_out=future(10))
        # Overlapping booking: days 7-12
        resp = self._create_booking(self.place_id, self.user_id,
                                    check_in=future(7), check_out=future(12))
        self.assertEqual(resp.status_code, 409)

    def test_create_booking_adjacent_no_conflict(self):
        """Booking starting exactly when another ends should not conflict."""
        self._create_booking(self.place_id, self.user_id,
                             check_in=future(5), check_out=future(8))
        resp = self._create_booking(self.place_id, self.user_id,
                                    check_in=future(8), check_out=future(12))
        self.assertEqual(resp.status_code, 201)

    # ── GET /api/v1/bookings/ ─────────────────────────────────────────────────

    def test_list_bookings(self):
        self._create_booking(self.place_id, self.user_id)
        resp = self.client.get('/api/v1/bookings/')
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.get_json(), list)

    # ── GET /api/v1/bookings/<id> ─────────────────────────────────────────────

    def test_get_booking_by_id(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        resp = self.client.get(f'/api/v1/bookings/{booking_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('guest_name', resp.get_json())
        self.assertIn('place_title', resp.get_json())

    def test_get_booking_not_found(self):
        resp = self.client.get('/api/v1/bookings/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── PUT /api/v1/bookings/<id> ─────────────────────────────────────────────

    def test_update_booking(self):
        booking_id = self._create_booking(
            self.place_id, self.user_id,
            check_in=future(5), check_out=future(8)
        ).get_json()['id']
        resp = self.client.put(f'/api/v1/bookings/{booking_id}', json={
            "place_id":  self.place_id,
            "user_id":   self.user_id,
            "check_in":  future(15),
            "check_out": future(20),
            "guests":    2,
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['guests'], 2)

    def test_update_booking_not_found(self):
        resp = self.client.put('/api/v1/bookings/nonexistent-id', json={
            "place_id":  self.place_id,
            "user_id":   self.user_id,
            "check_in":  future(5),
            "check_out": future(8),
            "guests":    1,
        })
        self.assertEqual(resp.status_code, 404)

    # ── DELETE /api/v1/bookings/<id> ──────────────────────────────────────────

    def test_delete_booking(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        resp = self.client.delete(f'/api/v1/bookings/{booking_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            self.client.get(f'/api/v1/bookings/{booking_id}').status_code, 404
        )

    def test_delete_booking_not_found(self):
        resp = self.client.delete('/api/v1/bookings/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── PATCH /api/v1/bookings/<id>/status ───────────────────────────────────

    def test_confirm_booking(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        resp = self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                                 json={"status": "confirmed"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['status'], 'confirmed')

    def test_cancel_booking(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        resp = self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                                 json={"status": "cancelled"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['status'], 'cancelled')

    def test_confirm_already_cancelled(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                          json={"status": "cancelled"})
        resp = self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                                 json={"status": "confirmed"})
        self.assertEqual(resp.status_code, 400)

    def test_cancel_already_cancelled(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                          json={"status": "cancelled"})
        resp = self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                                 json={"status": "cancelled"})
        self.assertEqual(resp.status_code, 400)

    def test_invalid_status_value(self):
        booking_id = self._create_booking(self.place_id, self.user_id).get_json()['id']
        resp = self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                                 json={"status": "flying"})
        self.assertIn(resp.status_code, [400, 422])

    def test_status_not_found(self):
        resp = self.client.patch('/api/v1/bookings/nonexistent-id/status',
                                 json={"status": "confirmed"})
        self.assertEqual(resp.status_code, 404)

    # ── Filtered views ────────────────────────────────────────────────────────

    def test_get_bookings_by_user(self):
        self._create_booking(self.place_id, self.user_id)
        resp = self.client.get(f'/api/v1/bookings/users/{self.user_id}')
        self.assertEqual(resp.status_code, 200)
        bookings = resp.get_json()
        self.assertTrue(all(b['user_id'] == self.user_id for b in bookings))

    def test_get_bookings_by_user_not_found(self):
        resp = self.client.get('/api/v1/bookings/users/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    def test_get_bookings_by_place(self):
        self._create_booking(self.place_id, self.user_id)
        resp = self.client.get(f'/api/v1/bookings/places/{self.place_id}')
        self.assertEqual(resp.status_code, 200)
        bookings = resp.get_json()
        self.assertTrue(all(b['place_id'] == self.place_id for b in bookings))

    def test_get_bookings_by_place_not_found(self):
        resp = self.client.get('/api/v1/bookings/places/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    # ── Cancelled booking does not block overlap check ────────────────────────

    def test_cancelled_booking_allows_new_overlap(self):
        booking_id = self._create_booking(
            self.place_id, self.user_id,
            check_in=future(5), check_out=future(10)
        ).get_json()['id']
        self.client.patch(f'/api/v1/bookings/{booking_id}/status',
                          json={"status": "cancelled"})
        # Same dates should now be accepted
        resp = self._create_booking(self.place_id, self.user_id,
                                    check_in=future(5), check_out=future(10))
        self.assertEqual(resp.status_code, 201)


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)
