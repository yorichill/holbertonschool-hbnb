from app.models.base_model import BaseModel
from app import db


class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), default='')

    def __init__(self, name, description=""):
        super().__init__()
        self.name = name
        self.description = description

    def to_dict(self):
        amenity_dict = super().to_dict()
        amenity_dict['name'] = self.name
        amenity_dict['description'] = self.description
        return amenity_dict
