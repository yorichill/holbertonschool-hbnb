from abc import ABC
import uuid
from datetime import datetime

class BaseModel(ABC):
    """
        BaseModel is the abstract base class for all application models.
    """

    def __init__(self):
        """Initialize BaseModel with unique ID and timestamps."""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def save(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now()

    def update(self, data):
        """
            Update instance attributes with provided data
            Args:
                data (dict): Dictionary of attributes to update
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def to_dict(self):
        """
            Convert instance to dictionary representation
            Returns:
                dict: Dictionary containing all attributes
        """
        # Start with base attributes
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        # Include all other attributes except private ones (those starting with _)
        for key, value in self.__dict__.items():
            if key not in ['id', 'created_at', 'updated_at']:
                result[key] = value

        return result
