from app.models.base_model import BaseModel
from app import db

class Place(BaseModel):
    __tablename__ = 'places'

    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default='')
    price = db.Column(db.Float, nullable=False)
    _latitude = db.Column('latitude', db.Float, nullable=False)
    _longitude = db.Column('longitude', db.Float, nullable=False)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    amenities = db.Column(db.JSON, default=list)

    def __init__(self, name, title, description, price, latitude, longitude, owner_id):
        super().__init__()
        self.name = name
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude    # passe par le setter avec validation
        self.longitude = longitude  # passe par le setter avec validation
        self.owner_id = owner_id
        self.amenities = []

    # ----------------- Latitude -----------------

    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if not isinstance(value, (int, float)) or not (-90 <= value <= 90):
            raise ValueError("Latitude must be a number between -90 and 90")
        self._latitude = value

    # ----------------- Longitude -----------------

    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if not isinstance(value, (int, float)) or not (-180 <= value <= 180):
            raise ValueError("Longitude must be a number between -180 and 180")
        self._longitude = value

    # ----------------- Amenities -----------------

    def add_amenity(self, amenity):
        amenity_id = amenity.id if hasattr(amenity, "id") else amenity
        if amenity_id not in self.amenities:
            self.amenities.append(amenity_id)

    # ----------------- Serialization -----------------

    def to_dict(self):
        place_dict = super().to_dict()
        place_dict['name'] = self.name
        place_dict['title'] = self.title
        place_dict['description'] = self.description
        place_dict['price'] = self.price
        place_dict['latitude'] = self.latitude
        place_dict['longitude'] = self.longitude
        place_dict['owner_id'] = self.owner_id
        place_dict['amenities'] = self.amenities
        return place_dict
