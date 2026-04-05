# HBnB – AirBnB Clone (Part 2)

A RESTful API built with Flask and flask-restx implementing the Presentation and Business Logic layers of the HBnB application.

## Project Structure

```
hbnb/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── api/
│   │   ├── v1/
│   │   │   ├── users.py     # User endpoints
│   │   │   ├── places.py    # Place endpoints
│   │   │   ├── reviews.py   # Review endpoints
│   │   │   └── amenities.py # Amenity endpoints
│   ├── models/
│   │   ├── base_model.py    # Shared BaseModel (uuid, timestamps)
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   └── amenity.py
│   ├── services/
│   │   ├── __init__.py      # Singleton facade instance
│   │   └── facade.py        # HBnBFacade – orchestrates all layers
│   └── persistence/
│       └── repository.py    # InMemoryRepository (replaced by DB in Part 3)
├── run.py                   # Entry point
├── config.py                # Environment config
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python run.py
```

The interactive Swagger UI is available at: **http://localhost:5000/api/v1/**

## API Endpoints

| Resource   | Method | Path                              | Description            |
|------------|--------|-----------------------------------|------------------------|
| Users      | POST   | `/api/v1/users/`                  | Create user            |
|            | GET    | `/api/v1/users/`                  | List all users         |
|            | GET    | `/api/v1/users/<id>`              | Get user by ID         |
|            | PUT    | `/api/v1/users/<id>`              | Update user            |
| Amenities  | POST   | `/api/v1/amenities/`              | Create amenity         |
|            | GET    | `/api/v1/amenities/`              | List all amenities     |
|            | GET    | `/api/v1/amenities/<id>`          | Get amenity by ID      |
|            | PUT    | `/api/v1/amenities/<id>`          | Update amenity         |
| Places     | POST   | `/api/v1/places/`                 | Create place           |
|            | GET    | `/api/v1/places/`                 | List all places        |
|            | GET    | `/api/v1/places/<id>`             | Get place by ID        |
|            | PUT    | `/api/v1/places/<id>`             | Update place           |
| Reviews    | POST   | `/api/v1/reviews/`                | Create review          |
|            | GET    | `/api/v1/reviews/`                | List all reviews       |
|            | GET    | `/api/v1/reviews/<id>`            | Get review by ID       |
|            | PUT    | `/api/v1/reviews/<id>`            | Update review          |
|            | DELETE | `/api/v1/reviews/<id>`            | Delete review          |
|            | GET    | `/api/v1/reviews/places/<id>/reviews` | Reviews for a place |
| Bookings   | POST   | `/api/v1/bookings/`               | Create booking         |
|            | GET    | `/api/v1/bookings/`               | List all bookings      |
|            | GET    | `/api/v1/bookings/<id>`           | Get booking by ID      |
|            | PUT    | `/api/v1/bookings/<id>`           | Update booking dates   |
|            | DELETE | `/api/v1/bookings/<id>`           | Delete booking         |
|            | PATCH  | `/api/v1/bookings/<id>/status`    | Confirm or cancel      |
|            | GET    | `/api/v1/bookings/users/<id>`     | Bookings by user       |
|            | GET    | `/api/v1/bookings/places/<id>`    | Bookings for a place   |

## Architecture

- **Presentation Layer** – flask-restx Namespaces with input validation and serialisation.
- **Business Logic Layer** – Plain Python model classes with validation in `__init__`.
- **Persistence Layer** – `InMemoryRepository` implementing a standard `Repository` ABC. Swappable with SQLAlchemy in Part 3.
- **Facade Pattern** – `HBnBFacade` is a singleton that decouples the API layer from storage details.
