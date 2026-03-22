from app import db
import uuid
from datetime import datetime

class BaseModel(db.Model):
    """Abstract base class for all application models."""

    __abstract__ = True  # SQLAlchemy ne crée pas de table pour BaseModel

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def save(self):
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.now()

    def update(self, data):
        """Update instance attributes with provided data."""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def to_dict(self):
        """Convert instance to dictionary representation."""
        result = {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        for key, value in self.__dict__.items():
            if not key.startswith('_') and key not in result:
                result[key] = value
        return result
