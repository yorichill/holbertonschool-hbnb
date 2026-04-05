from app.models.base_model import BaseModel
from app import db


class Review(BaseModel):
    __tablename__ = 'reviews'

    text     = db.Column(db.Text, nullable=False)
    rating   = db.Column(db.Integer, nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id  = db.Column(db.String(36), db.ForeignKey('users.id'),  nullable=False)

    def __init__(self, text: str = '', rating: int = 0,
                 place_id: str = '', user_id: str = '', **kwargs):
        super().__init__(**kwargs)
        if not text:
            raise ValueError("Review text cannot be empty.")
        if not (1 <= int(rating) <= 5):
            raise ValueError("Rating must be between 1 and 5.")
        if not place_id:
            raise ValueError("place_id is required.")
        if not user_id:
            raise ValueError("user_id is required.")
        self.text     = text
        self.rating   = int(rating)
        self.place_id = place_id
        self.user_id  = user_id

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            'text':     self.text,
            'rating':   self.rating,
            'place_id': self.place_id,
            'user_id':  self.user_id,
        })
        return base
    