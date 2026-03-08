from app.models import BaseModel

class Amenity(BaseModel):
    """
        Amenity model representing an amenity that can be associated with a place.
        E.g., "WiFi", "Pool", "Air Conditioning", Parking", etc.
    """

    def __init__(self, name, description=""):
        """
            Initialize an Amenity instance
            Args:
                name (str): Name of the amenity (e.g., "WiFi", "Pool")
                description (str): Optional description of the amenity
        """
        super().__init__() # Call __init__ of BaseModel
        self.name = name
        self.description = description

    def to_dict(self):
        """
            Convert Amenity to dictionary
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'name': self.name,
            'description': self.description
        }

    @staticmethod
    def list_all():
        """
            List all amenities
            Returns:
                list: List of all available Amenity objects
        """
        # Only a placeholder. In Part3, we will implement actual data retrieval.
        pass
