from app.models.base_model import BaseModel


class Amenity(BaseModel):
    """
    Represents a feature/amenity that can be attached to a Place.
    """

    def __init__(self, name: str = '', **kwargs):
        super().__init__(**kwargs)
        if not name or len(name) > 50:
            raise ValueError("Amenity name must be between 1 and 50 characters.")
        self.name = name

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({'name': self.name})
        return base
