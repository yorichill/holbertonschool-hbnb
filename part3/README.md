# HolbertonBnB (HBnB) — Part 2: Business Logic & REST API

A simplified AirBnB clone implementing a RESTful API and business logic layer using Python, Flask, and Flask-RESTx. The project is built on a modular, three-tier architecture that cleanly separates presentation, business logic, and persistence concerns — designed to scale toward database integration and authentication in future parts.

---

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Layered Architecture](#layered-architecture)
3. [Quick Start](#quick-start)
4. [Features](#features)
5. [API Endpoints](#api-endpoints)
6. [Code Walkthrough](#code-walkthrough)
7. [Design Patterns](#design-patterns)
8. [Testing](#testing)
9. [Project Vision](#project-vision)
10. [Technical Glossary](#technical-glossary)
11. [Resources](#resources)
12. [Authors](#authors)

---

## Project Architecture

```
hbnb/
├── run.py                          # Application entry point
├── config.py                       # Environment-based configuration
├── requirements.txt                # Python dependencies
│
├── app/
│   ├── __init__.py                 # Application Factory — create_app()
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py         # Namespace registration
│   │       ├── users.py            # User endpoints
│   │       ├── places.py           # Place endpoints
│   │       ├── reviews.py          # Review endpoints
│   │       ├── amenities.py        # Amenity endpoints
│   │       └── bookings.py         # Booking endpoints
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py           # Abstract parent class — id, timestamps, to_dict()
│   │   ├── user.py                 # User model — password property, email validation
│   │   ├── place.py                # Place model — GPS validation, amenities list
│   │   ├── review.py               # Review model — rating 1 to 5
│   │   ├── amenity.py              # Amenity model
│   │   └── booking.py              # Booking model — state machine, overlap detection
│   │
│   ├── services/
│   │   ├── __init__.py             # Singleton: facade = HBnBFacade()
│   │   └── facade.py               # HBnBFacade — orchestrator, 5 repositories
│   │
│   └── persistence/
│       ├── __init__.py
│       └── repository.py           # ABC Repository + InMemoryRepository (dict)
│
└── tests/
    └── test_hbnb_api.py            # Suite complète — Users, Places, Reviews, Amenities, Bookings
```

---

## Layered Architecture

The application strictly follows a **Three-Tier Architecture** where each layer has a single, clearly defined responsibility and no layer skips another.

```
+---------------------------------------------+
|         PRESENTATION LAYER (API)            |
|  app/api/v1/  ->  Flask-RESTx Namespaces    |
|  Receives HTTP requests, validates format   |
+--------------------+------------------------+
                     | calls
+--------------------v------------------------+
|             FACADE (HBnBFacade)             |
|  app/services/facade.py                     |
|  Single entry point — Singleton             |
+--------------------+------------------------+
                     | calls
+--------------------v------------------------+
|       BUSINESS LOGIC LAYER (Models)        |
|  app/models/  ->  User, Place, Review...   |
|  Business rules, data validation           |
+--------------------+------------------------+
                     | calls
+--------------------v------------------------+
|       PERSISTENCE LAYER (Repository)       |
|  app/persistence/repository.py             |
|  InMemoryRepository — Python dict in RAM   |
+---------------------------------------------+
```

**Essential flow:**

```
HTTP Request -> API (flask-restx) -> Facade (HBnBFacade) -> Model / Repository -> JSON Response
```

### Layer responsibilities

| Layer | Folder | Responsibility | Does NOT know about |
|-------|--------|----------------|---------------------|
| Presentation | `app/api/v1/` | Receive HTTP requests, validate payload format, return JSON | How data is stored |
| Business Logic | `app/models/` | Business rules, entity validation, relationships | Flask, HTTP, storage |
| Persistence | `app/persistence/` | Store and retrieve data | Business rules, API |

---

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd holbertonschool-hbnb/part2/hbnb
   ```

2. **Set up a virtual environment** (recommended)
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python run.py
```

The API will be available at:

- **API Base URL**: `http://localhost:5000/api/v1/`
- **Interactive Swagger Documentation**: `http://localhost:5000/api/v1/`

### Running the Tests

```bash
python -m pytest tests/test_hbnb_api.py -v
# or
python -m unittest tests/test_hbnb_api.py
```

### Dependencies

```
flask>=2.0.0        # Web framework
flask-restx>=1.0.0  # REST API extension with Swagger documentation
```

---

## Features

### Core Functionality

- **User Management**: Create, read, and update users with email validation and secure password handling
- **Place Management**: Properties with GPS coordinates, pricing, owner, and linked amenities
- **Review System**: User reviews with ratings (1–5) for places, full CRUD including DELETE
- **Amenity Management**: Configurable amenities that can be attached to places
- **Booking System**: Reservations with date conflict detection, state machine (pending / confirmed / cancelled), and enriched responses

### Technical Features

- **RESTful API Design**: Clean, consistent endpoint structure following REST principles
- **Two-Level Validation**: Format validation at the API layer (flask-restx) + business rule validation at the model layer
- **Data Serialization**: `to_dict()` on every model converts Python objects to JSON-compatible dicts, excluding sensitive fields
- **Modular Architecture**: Each layer is independently testable and replaceable
- **Auto-generated Documentation**: Interactive Swagger/OpenAPI UI at the root URL
- **State Machine**: `Booking` enforces legal status transitions — `cancelled` is a terminal state
- **Overlap Detection**: `_check_overlap()` prevents double-booking using the interval algorithm: `[A,B]` and `[C,D]` overlap iff `A < D AND B > C`

---

## API Endpoints

The Swagger UI is available at `http://localhost:5000/api/v1/` and allows testing all endpoints interactively.

### Users `/api/v1/users/`

| Method | URL | Description | Success Code |
|--------|-----|-------------|--------------|
| `POST` | `/api/v1/users/` | Create a user | 201 |
| `GET` | `/api/v1/users/` | List all users | 200 |
| `GET` | `/api/v1/users/<id>` | Get user by ID | 200 |
| `PUT` | `/api/v1/users/<id>` | Update a user | 200 |

**Example — POST /api/v1/users/**

```json
// Request body:
{
  "first_name": "Arnaud",
  "last_name": "Messenet",
  "email": "arnaud.messenet@example.com",
  "password": "password123"
}

// Response 201:
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "first_name": "Arnaud",
  "last_name": "Messenet",
  "email": "arnaud.messenet@example.com",
  "is_admin": false
}
```

> Note: `_password` is never returned in any response. The `password` property getter always returns `None`.

---

### Places `/api/v1/places/`

| Method | URL | Description | Success Code |
|--------|-----|-------------|--------------|
| `POST` | `/api/v1/places/` | Create a place | 201 |
| `GET` | `/api/v1/places/` | List all places | 200 |
| `GET` | `/api/v1/places/<id>` | Get place details with owner and amenities | 200 |
| `PUT` | `/api/v1/places/<id>` | Update a place | 200 |

**Example — GET /api/v1/places/\<id\> (enriched response)**

```json
{
  "id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Cosy Apartment",
  "description": "A great place",
  "price": 100.0,
  "latitude": 48.8566,
  "longitude": 2.3522,
  "owner": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "first_name": "Thomas",
    "last_name": "Haenel"
  },
  "amenities": ["wifi-uuid", "pool-uuid"]
}
```

> Validation: `price >= 0`, `latitude` in `[-90, 90]`, `longitude` in `[-180, 180]`. Invalid values raise `ValueError` → HTTP 400.

---

### Reviews `/api/v1/reviews/`

| Method | URL | Description | Success Code |
|--------|-----|-------------|--------------|
| `POST` | `/api/v1/reviews/` | Create a review | 201 |
| `GET` | `/api/v1/reviews/` | List all reviews | 200 |
| `GET` | `/api/v1/reviews/<id>` | Get a review by ID | 200 |
| `PUT` | `/api/v1/reviews/<id>` | Update a review | 200 |
| `DELETE` | `/api/v1/reviews/<id>` | Delete a review | 200 |
| `GET` | `/api/v1/reviews/places/<id>/reviews` | All reviews for a place | 200 |

> Validation: `text` cannot be empty, `rating` must be an integer between 1 and 5 inclusive. Both `user_id` and `place_id` must exist — otherwise 404.

---

### Amenities `/api/v1/amenities/`

| Method | URL | Description | Success Code |
|--------|-----|-------------|--------------|
| `POST` | `/api/v1/amenities/` | Create an amenity | 201 |
| `GET` | `/api/v1/amenities/` | List all amenities | 200 |
| `GET` | `/api/v1/amenities/<id>` | Get an amenity by ID | 200 |
| `PUT` | `/api/v1/amenities/<id>` | Update an amenity | 200 |

---

### Bookings `/api/v1/bookings/`

| Method | URL | Description | Success Code |
|--------|-----|-------------|--------------|
| `POST` | `/api/v1/bookings/` | Create a booking | 201 |
| `GET` | `/api/v1/bookings/` | List all bookings | 200 |
| `GET` | `/api/v1/bookings/<id>` | Get a booking (enriched) | 200 |
| `PUT` | `/api/v1/bookings/<id>` | Update dates / guests | 200 |
| `DELETE` | `/api/v1/bookings/<id>` | Delete a booking | 200 |
| `PATCH` | `/api/v1/bookings/<id>/status` | Confirm or cancel a booking | 200 |
| `GET` | `/api/v1/bookings/users/<id>` | All bookings for a user | 200 |
| `GET` | `/api/v1/bookings/places/<id>` | All bookings for a place | 200 |

> `PATCH` is used for status transitions (not `PUT`) because only the `status` field is modified. Using `PUT` would require sending the entire resource and would semantically imply a full replacement.

---

### HTTP Status Codes

| Code | Meaning | When used |
|------|---------|-----------|
| 200 | Success | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST — new resource created |
| 400 | Bad Request | Missing / invalid data, or business rule violated (ValueError) |
| 404 | Not Found | Resource does not exist — unknown UUID |
| 409 | Conflict | Booking date overlap — request is format-valid but conflicts with server state |

> **Why 409 and not 400 for overlapping dates?** A `400` means the request is malformed. A `409` means the request is valid but conflicts with the current server state. A booking with overlapping dates has a perfectly valid format — it simply cannot be created because those dates are already taken.

---

## Code Walkthrough

### `run.py` — Entry Point

```python
from app import create_app
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
```

This file is the first executed when running `python run.py`. It calls `create_app()` — the **Application Factory** pattern — which assembles the entire Flask application. `debug=True` enables automatic server reload on file changes and displays detailed error messages. Never use `debug=True` in production.

---

### `config.py` — Configuration

```python
import os
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DEBUG = False
class DevelopmentConfig(Config):
    DEBUG = True
config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
```

`os.getenv()` reads values from system environment variables with a fallback default. This is a security best practice — secrets are never hardcoded in source code. `DevelopmentConfig` inherits from `Config` and overrides `DEBUG = True`, demonstrating Python inheritance.

---

### `app/services/__init__.py` — Facade Singleton

```python
from app.services.facade import HBnBFacade
facade = HBnBFacade()
```

These two lines create **one single instance** of `HBnBFacade` at module load time. Python caches modules — every `from app.services import facade` retrieves the **same object** with the same repositories. This is the **Singleton Pattern**: one single source of truth for all data in RAM.

---

### `app/persistence/repository.py` — Repository & InMemoryRepository

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def add(self, obj): pass

    @abstractmethod
    def get(self, obj_id): pass

    @abstractmethod
    def get_all(self): pass

    @abstractmethod
    def update(self, obj_id, data): pass

    @abstractmethod
    def delete(self, obj_id): pass

    @abstractmethod
    def get_by_attribute(self, attr_name, attr_value): pass

class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}            # { "uuid-string": Python instance }

    def add(self, obj):
        self._storage[obj.id] = obj   # O(1) insertion

    def get(self, obj_id):
        return self._storage.get(obj_id)  # O(1) — returns None if not found

    def get_all(self):
        return list(self._storage.values())

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            obj.update(data)          # Delegates to BaseModel.update()

    def delete(self, obj_id):
        if obj_id in self._storage:
            del self._storage[obj_id]

    def get_by_attribute(self, attr_name, attr_value):
        return next(
            (obj for obj in self._storage.values()
             if getattr(obj, attr_name) == attr_value),
            None
        )
```

`Repository` is an **ABC** — it defines a **contract** of 6 abstract methods that every subclass must implement. `InMemoryRepository` fulfills this contract using a Python `dict` as an in-RAM database. **Why dict and not list?** `dict[uuid]` = O(1) access. `list.find(uuid)` = O(n) — scanning all elements. In Part 3, `InMemoryRepository` is replaced by `SQLAlchemyRepository` without touching the API or model layers.

---

### `app/models/base_model.py` — Abstract Parent Class

```python
from abc import ABC
import uuid
from datetime import datetime

class BaseModel(ABC):
    def __init__(self):
        self.id = str(uuid.uuid4())       # Unique UUID4 identifier
        self.created_at = datetime.now()  # Creation timestamp
        self.updated_at = datetime.now()  # Last-updated timestamp

    def save(self):
        self.updated_at = datetime.now()

    def update(self, data):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)  # Dynamic attribute assignment
        self.save()

    def to_dict(self):
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        for key, value in self.__dict__.items():
            if key not in ['id', 'created_at', 'updated_at']:
                result[key] = value
        return result
```

`BaseModel` is the **abstract parent class** for all models (`User`, `Place`, `Review`, `Amenity`, `Booking`). It automatically provides a UUID4 identifier, two ISO 8601 timestamps, partial update via `update()`, and JSON serialization via `to_dict()`. This is the **DRY** principle — common code written once and inherited by all five models.

---

### `app/models/user.py` — User Model

```python
import re
from app.models import BaseModel

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password       # Passes through @password.setter
        self.is_admin = is_admin

    @property
    def password(self):
        return None                    # Never return the real password

    @password.setter
    def password(self, value):
        self._password = value         # Stored in private attribute

    def validate_email(self):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, self.email) is not None

    def to_dict(self):
        user_dict = super().to_dict()
        user_dict['first_name'] = self.first_name
        user_dict['last_name'] = self.last_name
        user_dict['email'] = self.email
        user_dict['is_admin'] = self.is_admin
        user_dict.pop('_password', None)   # Exclude password from response
        return user_dict
```

The `@property` decorator makes `password` a validated attribute. The **getter always returns `None`** — the real password is never exposed. The **setter stores the value in `_password`** (private by convention). `to_dict()` explicitly removes `_password` using `pop()`, ensuring the password never appears in any HTTP response.

---

### `app/models/place.py` — Place Model

```python
class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner_id):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self._latitude = latitude         # Private attribute
        self._longitude = longitude       # Private attribute
        self.owner_id = owner_id
        self.amenities = []               # List of amenity UUIDs

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if not (-90 <= value <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        self._latitude = value

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if not (-180 <= value <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        self._longitude = value
```

`Place` uses **property setters** for GPS validation — latitude must be in `[-90, 90]`, longitude in `[-180, 180]`. If an invalid value is passed, a `ValueError` is raised immediately inside the constructor and bubbles up to the endpoint, which converts it to a `400 Bad Request`. This is **encapsulation**: validation is hidden behind a simple assignment interface (`place.latitude = value`).

---

### `app/models/booking.py` — Booking Model (State Machine)

```python
class Booking(BaseModel):
    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    def __init__(self, place_id, user_id, check_in, check_out, guests=1):
        super().__init__()
        self.check_in  = self._parse_date(check_in,  'check_in')
        self.check_out = self._parse_date(check_out, 'check_out')
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be strictly after check_in.")
        if self.check_in < date.today():
            raise ValueError("check_in cannot be in the past.")
        if int(guests) < 1:
            raise ValueError("guests must be at least 1.")
        self.status = self.STATUS_PENDING      # Always starts as pending

    @property
    def nights(self):
        return (self.check_out - self.check_in).days   # Computed dynamically

    def confirm(self):
        if self.status != self.STATUS_PENDING:
            raise ValueError("Only pending bookings can be confirmed.")
        self.status = self.STATUS_CONFIRMED

    def cancel(self):
        if self.status == self.STATUS_CANCELLED:
            raise ValueError("Booking is already cancelled.")
        self.status = self.STATUS_CANCELLED
```

`Booking` implements a **state machine**. Legal transitions: `pending → confirmed`, `pending → cancelled`, `confirmed → cancelled`. The `cancelled` state is **terminal** — there is no way out. The `nights` property is computed dynamically without storing a value. Class constants (`STATUS_PENDING`, etc.) avoid magic strings — a typo like `'pendng'` would raise an `AttributeError` rather than silently fail.

---

### `app/services/facade.py` — The Facade

```python
class HBnBFacade:
    def __init__(self):
        self.user_repo    = InMemoryRepository()
        self.place_repo   = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()
        self.review_repo  = InMemoryRepository()
        self.booking_repo = InMemoryRepository()

    def create_user(self, user_data):
        user = User(**user_data)       # Instantiate + validate
        self.user_repo.add(user)       # Persist
        return user

    def create_place(self, place_data):
        owner = self.user_repo.get(place_data.get('owner_id'))
        if not owner:
            raise ValueError("Owner not found.")
        place = Place(...)
        self.place_repo.add(place)
        return place

    def _check_overlap(self, new_booking, exclude_id=None):
        for b in self.booking_repo.get_all():
            if b.place_id != new_booking.place_id:
                continue
            if b.status == 'cancelled':        # Cancelled bookings free the dates
                continue
            # Two intervals [A,B] and [C,D] overlap iff A < D AND B > C
            if new_booking.check_in < b.check_out and \
               new_booking.check_out > b.check_in:
                raise ValueError("Dates conflict with existing booking.")
```

`HBnBFacade` is the **orchestrator**. It owns 5 repositories (one per entity), exposes high-level methods to the API layer (`create_user`, `create_place`, `create_booking`...), and centralizes cross-cutting rules like date overlap detection. API endpoints call the Facade — they have **no direct knowledge of repositories**.

---

### `app/api/v1/users.py` — User Endpoints

```python
from flask_restx import Namespace, Resource, abort
from app.services import facade

api = Namespace('users', description='User operations')

@api.route('/')
class UserList(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = facade.create_user(data)
            return user.to_dict(), 201
        except ValueError as e:
            abort(400, message=str(e))     # ValueError -> 400

    def get(self):
        return [u.to_dict() for u in facade.user_repo.get_all()], 200

@api.route('/<string:user_id>')
class UserDetail(Resource):
    def get(self, user_id):
        user = facade.user_repo.get(user_id)
        if not user:
            abort(404, message="User not found")
        return user.to_dict(), 200
```

Each class inherits from `Resource` (flask-restx). The methods `get()`, `post()`, `put()` map directly to HTTP verbs. The flow is: receive request → call facade → `try/except` (`ValueError` → 400) → `to_dict()` → JSON + status code. `abort()` immediately halts execution and sends the error response.

---

### `app/api/v1/bookings.py` — Booking Status Endpoint

```python
@api.route('/<string:booking_id>/status')
class BookingStatus(Resource):
    @api.expect(status_model, validate=True)
    def patch(self, booking_id):
        booking = _get_or_404(booking_id)
        new_status = api.payload['status']
        try:
            if new_status == 'confirmed':
                booking.confirm()      # State machine transition
            elif new_status == 'cancelled':
                booking.cancel()
        except ValueError as e:
            api.abort(400, str(e))     # Illegal transition -> 400
        return _enrich(booking), 200

def _enrich(booking):
    data = booking.to_dict()
    place = facade.get_place(booking.place_id)
    user  = facade.get_user(booking.user_id)
    if place:
        data['place_title']     = place.title
        data['price_per_night'] = place.price
        data['total_price']     = round(place.price * booking.nights, 2)
    if user:
        data['guest_name'] = f'{user.first_name} {user.last_name}'
    return data
```

`PATCH` is used instead of `PUT` because only the `status` field changes — a partial update, not a full resource replacement. `_enrich()` adds computed data to the response: place title, guest name, and total price (`price_per_night × nights`). This avoids N+1 API calls — the client gets all needed information in a single response.

---

## Design Patterns

| Pattern | Where used | What it solves |
|---------|-----------|----------------|
| **Facade** | `app/services/facade.py` | Provides a single, simplified interface to all business operations. Endpoints never touch repositories directly. |
| **Repository** | `app/persistence/repository.py` | Abstracts storage behind a generic interface. Swap `InMemoryRepository` for `SQLAlchemyRepository` in Part 3 by changing one line in `facade.py`. |
| **Singleton** | `app/services/__init__.py` | Ensures one shared `HBnBFacade` instance across the entire application — one source of truth for all RAM data. |
| **Application Factory** | `app/__init__.py` | Creates the Flask app inside `create_app()`, allowing multiple instances with different configurations (dev, prod, test). |
| **ABC / Interface** | `app/persistence/repository.py`, `app/models/base_model.py` | Defines contracts via `@abstractmethod`. Any class that skips an implementation raises `TypeError` at instantiation. |
| **State Machine** | `app/models/booking.py` | Enforces legal status transitions (`pending → confirmed/cancelled`). `cancelled` is terminal. Illegal transitions raise `ValueError → 400`. |

---

## Testing

Tests use Python's built-in `unittest` library and the **Flask test client**. No real server is launched — `app.test_client()` simulates HTTP requests in memory. All tests are grouped in a single file: `tests/test_hbnb_api.py`.

```python
def setUp(self):
    self.app = create_app()             # Fresh application instance
    self.client = self.app.test_client()
```

`setUp()` is called before **every single test**, creating a fresh application with empty repositories. Data created in one test never bleeds into another.

### Test users

The test suite uses the three team members as test identities, each with a defined role:

| User | Email | Role in tests |
|------|-------|---------------|
| **Arnaud Messenet** | `arnaud.messenet@example.com` | Owner / host — creates places |
| **Valentin Dardenne** | `valentin.dardenne@example.com` | Guest — makes bookings and reviews |
| **Thomas Haenel** | `thomas.haenel@example.com` | Second owner — used in update and multi-user scenarios |

### What is tested

| Class | Test cases |
|-------|-----------|
| `TestUsers` | 201 success, 400 (empty name, invalid email, duplicate email), 200/404 GET, 200/404 PUT |
| `TestPlaces` | 201 success, 400 (empty title, negative price, invalid GPS, unknown owner), boundary lat/lon (-90/90, -180/180), 200/404 GET and PUT |
| `TestReviews` | 201 success, 400 (empty text, rating 0 or 6, unknown user/place), 200/404 GET and PUT, 200/404 DELETE, GET reviews by place |
| `TestAmenities` | 201 success, 400 (empty name, missing name), 200/404 GET and PUT |
| `TestBookings` | 201, 404 (invalid place/user), 400 (check_out <= check_in, guests=0, past check_in), **409** (date overlap), 201 (adjacent dates allowed), state transitions (confirm/cancel), 400 (illegal transition), DELETE, GET by user/place, cancelled booking frees dates |

### Example test — cURL

```bash
# Create a user (Arnaud as owner)
curl -X POST http://localhost:5000/api/v1/users/ \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Arnaud", "last_name": "Messenet", "email": "arnaud.messenet@example.com", "password": "pass"}'

# Create a user (Valentin as guest)
curl -X POST http://localhost:5000/api/v1/users/ \
     -H "Content-Type: application/json" \
     -d '{"first_name": "Valentin", "last_name": "Dardenne", "email": "valentin.dardenne@example.com", "password": "pass"}'

# List all places
curl -X GET http://localhost:5000/api/v1/places/

# Create a booking
curl -X POST http://localhost:5000/api/v1/bookings/ \
     -H "Content-Type: application/json" \
     -d '{"place_id": "<place_id>", "user_id": "<user_id>", "check_in": "2026-04-01", "check_out": "2026-04-05", "guests": 2}'

# Confirm a booking
curl -X PATCH http://localhost:5000/api/v1/bookings/<booking_id>/status \
     -H "Content-Type: application/json" \
     -d '{"status": "confirmed"}'
```

---

## Project Vision

### Current Phase — Part 2

- RESTful API with full CRUD operations for all five entities
- Business logic with two-level validation (format + business rules)
- In-memory persistence with the Repository Pattern
- Modular three-tier architecture ready for extension

### Future Phases

- **Part 3**: Database integration with SQLAlchemy — replace `InMemoryRepository` by swapping one line in `facade.py`
- **Part 4**: JWT authentication and authorization — add `@jwt_required` decorators without modifying business logic

---

## Technical Glossary

| Term | Definition |
|------|-----------|
| **ABC (Abstract Base Class)** | Python class defining a contract via `@abstractmethod`. Cannot be instantiated directly. Any subclass missing an abstract method raises `TypeError`. |
| **Application Factory** | Flask pattern where the app is created in `create_app()` rather than at module level. Enables multiple instances for testing and different environments. |
| **CRUD** | Create, Read, Update, Delete — the four fundamental data operations. Maps to POST, GET, PUT/PATCH, DELETE. |
| **DRY (Don't Repeat Yourself)** | Every logic written only once. Applied via `BaseModel` — common code inherited by all five models. |
| **Encapsulation** | OOP principle hiding internal details and exposing only a simple interface. Example: `_latitude` + `@property` setter. |
| **Facade Pattern** | Provides a simplified interface to a complex system. `HBnBFacade` hides repositories and centralizes business logic. |
| **Idempotence** | Property of an operation that produces the same result whether executed once or multiple times. GET, PUT, and DELETE are idempotent. POST is not. |
| **InMemoryRepository** | Concrete Repository implementation using a Python `dict` as in-RAM storage. O(1) access by UUID key. Data is lost on server restart. |
| **JSON** | JavaScript Object Notation. Lightweight key-value text format. Universal standard for REST API data exchange. |
| **Machine à états / State Machine** | System where an object can be in only one state at a time, with defined transitions. Used for `Booking.status`. |
| **O(1) / O(n)** | Big O complexity notation. O(1) = constant time (dict lookup). O(n) = proportional to data size (list scan). |
| **Open/Closed Principle** | Software should be open for extension but closed for modification. The Repository Pattern + ABC enables adding `SQLAlchemyRepository` without changing existing code. |
| **@property** | Python decorator turning a method into a computed or validated attribute. Enables transparent validation on assignment. |
| **Repository Pattern** | Abstracts data access behind a generic interface. Business code does not know whether data is stored in RAM, SQL, or MongoDB. |
| **REST** | Representational State Transfer. Architectural style for web APIs based on HTTP, stateless requests, and resource-oriented URLs. |
| **Serialization** | Converting a Python object to a JSON-compatible dict. Performed by `to_dict()` on each model before returning an HTTP response. |
| **Singleton** | Pattern ensuring a class has only one instance throughout the application. `facade = HBnBFacade()` in `services/__init__.py`. |
| **Three-Tier Architecture** | Industry-standard pattern: Presentation / Business Logic / Persistence. Each layer has one responsibility and does not skip another. |
| **Two-Level Validation** | Level 1: flask-restx validates format and field presence. Level 2: model `__init__` validates business rules. `ValueError` → caught by `try/except` → HTTP 400. |
| **UUID4** | Universally Unique Identifier, version 4 — fully random 128-bit identifier. Generated via `str(uuid.uuid4())`. Globally unique, no database needed, enumeration-resistant. |
| **ValueError** | Python exception raised when a value has the right type but is unacceptable (e.g. `rating > 5`, `latitude > 90`, `check_out <= check_in`). Converted to HTTP 400 in endpoints. |

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask-RESTx Documentation](https://flask-restx.readthedocs.io/en/latest/)
- [REST API Best Practices](https://restfulapi.net/)
- [Python Project Structure Guide](https://docs.python-guide.org/writing/structure/)
- [Facade Pattern in Python](https://refactoring.guru/design-patterns/facade/python/example)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is part of the Holberton School curriculum.

---

## Authors

- [Arnaud Messenet](https://github.com/Crypoune) &nbsp;&nbsp; [![Badge](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/Crypoune)
- [Thomas Haenel](https://github.com/yorichill) &nbsp;&nbsp; [![Badge](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/yorichill)
- [Valentin Dardenne](https://github.com/ValentinDLC) &nbsp;&nbsp; [![Badge](https://badgen.net/badge/icon/github?icon=github&label)](https://github.com/ValentinDLC)

---
