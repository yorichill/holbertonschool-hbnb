import uuid
from datetime import datetime
from app import db


class BaseModel(db.Model):
    __abstract__ = True

    _PROTECTED = frozenset({'id', 'created_at', 'updated_at'})

    id         = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            if key not in self._PROTECTED:
                setattr(self, key, value)

    def update(self, data: dict):
        for key, value in data.items():
            if key in self._PROTECTED:
                continue
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            'id':         self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self.id}>"