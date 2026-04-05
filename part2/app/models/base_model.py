import uuid
from datetime import datetime


class BaseModel:
    """
    Base class for all models.

    Accepts **kwargs so subclasses (and SQLAlchemy in Part 3) can be
    instantiated dynamically from a dict without touching every constructor.

    Reserved keys handled here:
        id, created_at, updated_at  →  never overwritten by kwargs
    """

    # Fields that must never be set via kwargs from outside
    _PROTECTED = frozenset({'id', 'created_at', 'updated_at'})

    def __init__(self, **kwargs):
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

        # Apply any extra kwargs that aren't protected
        for key, value in kwargs.items():
            if key not in self._PROTECTED:
                setattr(self, key, value)

    def update(self, data: dict):
        """
        Partial update: apply every key in *data* that the object already
        owns, skipping protected fields.  Bumps updated_at automatically.
        """
        for key, value in data.items():
            if key in self._PROTECTED:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """
        Minimal serialisation shared by all models.
        Subclasses extend or override this.
        """
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        """
        Factory: build an instance from a plain dict.
        Useful for deserialization and future DB row → object mapping.

        Example
        -------
        user = User.from_dict({'first_name': 'Alice', 'email': '...'})
        """
        return cls(**data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"
