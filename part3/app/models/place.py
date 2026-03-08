from app.models import BaseModel

class Place(BaseModel):
    """
    Place model representing a place to stay.
    """

    def __init__(self, name, title, description, price, latitude, longitude, owner_id):
        """
        Initialize a Place instance.
        Args:
            name (str): Short identifier for the place (e.g., "Cozy Cottage")
            title (str): Full marketing title (e.g., "Cozy Cottage in the Woods")
            description (str): Detailed description
            price (float): Price per night
            latitude (float): GPS latitude (-90 to 90)
            longitude (float): GPS longitude (-180 to 180)
            owner_id (str): UUID of the owner
        """
        super().__init__()
        self.name = name
        self.title = title
        self.description = description
        self.price = price
        self._latitude = latitude
        self._longitude = longitude
        self.owner_id = owner_id
        self.amenities = []  # List of amenity IDs (UUID strings)

    # ----------------- Latitude -----------------
    @property
    def latitude(self):
        """Getter for latitude"""
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        if not isinstance(value, (int, float)) or not (-90 <= value <= 90):
            raise ValueError("Latitude must be a number between -90 and 90")
        self._latitude = value

    # ----------------- Longitude -----------------
    @property
    def longitude(self):
        """Getter for longitude"""
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        if not isinstance(value, (int, float)) or not (-180 <= value <= 180):
            raise ValueError("Longitude must be a number between -180 and 180")
        self._longitude = value

    # ----------------- Amenities -----------------
    def add_amenity(self, amenity):
        """
        Add an amenity to the place.
        Accepts either an Amenity object or its id (string).
        """
        if hasattr(amenity, "id"):
            amenity_id = amenity.id
        else:
            amenity_id = amenity  # assume it's a UUID string

        if amenity_id not in self.amenities:
            self.amenities.append(amenity_id)

    # ----------------- Serialization -----------------
    def to_dict(self):
        """
        Convert Place to dictionary.
        Includes private coordinates and amenity IDs.
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'name': self.name,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'latitude': self._latitude,
            'longitude': self._longitude,
            'owner_id': self.owner_id,
            'amenities': self.amenities
        }

    # ----------------- Static / Class Methods -----------------
    @staticmethod
    def list_all():
        """List all places (to be implemented in Part3)"""
        pass

    @staticmethod
    def get_by_criteria(criteria):
        """
        Get places by search criteria (to be implemented in Part3)
        Args:
            criteria (dict): filters like price_max, city, etc.
        Returns:
            list of Place objects
        """
        pass

    def get_all_reservations(self):
        """
        Get all reservations for this place (to be implemented in Part3)
        Private method for owner use only
        """
        pass