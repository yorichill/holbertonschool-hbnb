from datetime import date
from app.models.base_model import BaseModel
from app import db


class Booking(BaseModel):
    __tablename__ = 'bookings'

    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'

    place_id  = db.Column(db.String(36), db.ForeignKey('places.id'), nullable=False)
    user_id   = db.Column(db.String(36), db.ForeignKey('users.id'),  nullable=False)
    check_in  = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    guests    = db.Column(db.Integer, nullable=False, default=1)
    status    = db.Column(db.String(20), nullable=False, default='pending')

    def __init__(self, place_id='', user_id='', check_in='', check_out='', guests=1, **kwargs):
        super().__init__(**kwargs)
        self.check_in  = self._parse_date(check_in,  'check_in')
        self.check_out = self._parse_date(check_out, 'check_out')
        if self.check_out <= self.check_in:
            raise ValueError("check_out must be strictly after check_in.")
        if self.check_in < date.today():
            raise ValueError("check_in cannot be in the past.")
        if int(guests) < 1:
            raise ValueError("guests must be at least 1.")
        if not place_id:
            raise ValueError("place_id is required.")
        if not user_id:
            raise ValueError("user_id is required.")
        self.place_id = place_id
        self.user_id  = user_id
        self.guests   = int(guests)
        self.status   = self.STATUS_PENDING

    @staticmethod
    def _parse_date(value, field):
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be a valid date (YYYY-MM-DD).")

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    def confirm(self):
        if self.status != self.STATUS_PENDING:
            raise ValueError("Only pending bookings can be confirmed.")
        self.status = self.STATUS_CONFIRMED
        from app import db
        db.session.commit()

    def cancel(self):
        if self.status == self.STATUS_CANCELLED:
            raise ValueError("Booking is already cancelled.")
        self.status = self.STATUS_CANCELLED
        from app import db
        db.session.commit()

    def to_dict(self):
        base = super().to_dict()
        base.update({
            'place_id':  self.place_id,
            'user_id':   self.user_id,
            'check_in':  self.check_in.isoformat(),
            'check_out': self.check_out.isoformat(),
            'nights':    self.nights,
            'guests':    self.guests,
            'status':    self.status,
        })
        return base