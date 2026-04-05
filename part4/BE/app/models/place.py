from app.models.base_model import BaseModel
from app import db
place_amenity = db.Table(
    'place_amenity',
    db.Column('place_id',   db.String(36), db.ForeignKey('places.id'),    primary_key=True),
    db.Column('amenity_id', db.String(36), db.ForeignKey('amenities.id'), primary_key=True),
)


class Place(BaseModel):
    __tablename__ = 'places'

    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text,        nullable=True)
    price       = db.Column(db.Float,       nullable=False)
    latitude    = db.Column(db.Float,       nullable=False)
    longitude   = db.Column(db.Float,       nullable=False)
    owner_id    = db.Column(db.String(36),  db.ForeignKey('users.id'), nullable=False)

    reviews   = db.relationship('Review',  backref='place', lazy=True, cascade='all, delete-orphan')
    bookings  = db.relationship('Booking', backref='place', lazy=True, cascade='all, delete-orphan')
    amenities = db.relationship('Amenity', secondary=place_amenity,
                                 lazy='subquery',
                                 backref=db.backref('places', lazy=True))

    def __init__(self, title='', description='', price=0.0,
                 latitude=0.0, longitude=0.0, owner_id='', **kwargs):
        super().__init__(**kwargs)
        if not title or len(title) > 100:
            raise ValueError("Title must be between 1 and 100 characters.")
        if float(price) < 0:
            raise ValueError("Price must be a non-negative value.")
        if not (-90.0 <= float(latitude) <= 90.0):
            raise ValueError("Latitude must be between -90 and 90.")
        if not (-180.0 <= float(longitude) <= 180.0):
            raise ValueError("Longitude must be between -180 and 180.")
        if not owner_id:
            raise ValueError("owner_id is required.")
        self.title       = title
        self.description = description
        self.price       = float(price)
        self.latitude    = float(latitude)
        self.longitude   = float(longitude)
        self.owner_id    = owner_id

    def to_dict(self, include_owner=False, owner=None):
        base = super().to_dict()
        base.update({
            'title':          self.title,
            'name':           self.title,        # alias front
            'description':    self.description,
            'price':          self.price,
            'price_by_night': self.price,        # alias front
            'latitude':       self.latitude,
            'longitude':      self.longitude,
            'owner_id':       self.owner_id,
            'amenities':      [a.to_dict() for a in self.amenities],
        })
        if include_owner and owner:
            base['owner'] = {
                'id':         owner.id,
                'first_name': owner.first_name,
                'last_name':  owner.last_name,
                'email':      owner.email,
            }
        return base

    # alias pour compatibilité front
    @property
    def price_by_night(self):
        return self.price