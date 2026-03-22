from app.models.base_model import BaseModel
from app import db


class Review(BaseModel):
    __tablename__ = 'reviews'

    text = db.Column(db.String(1000), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    place_id = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)

    def __init__(self, text, rating, user_id, place_id):
        super().__init__()
        self.text = text
        self.rating = rating
        self.user_id = user_id
        self.place_id = place_id
        self.validate_rating()

    def validate_rating(self):
        if not isinstance(self.rating, int) or not (1 <= self.rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")

    def to_dict(self):
        review_dict = super().to_dict()
        review_dict['text'] = self.text
        review_dict['rating'] = self.rating
        review_dict['user_id'] = self.user_id
        review_dict['place_id'] = self.place_id
        return review_dict
