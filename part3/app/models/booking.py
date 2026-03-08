from datetime import date
from app.models import BaseModel


class Booking(BaseModel):
    """
    Represents a reservation made by a user for a place.

    Status lifecycle:  pending → confirmed
                       pending → cancelled
                    confirmed → cancelled
    """

    STATUS_PENDING   = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_CANCELLED = 'cancelled'
    VALID_STATUSES   = {STATUS_PENDING, STATUS_CONFIRMED, STATUS_CANCELLED}

    def __init__(self, place_id: str = '', user_id: str = '',
                 check_in: str = '', check_out: str = '',
                 guests: int = 1, **kwargs):
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

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _parse_date(value, field: str) -> date:
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            raise ValueError(f"{field} must be a valid date (YYYY-MM-DD).")

    @property
    def nights(self) -> int:
        return (self.check_out - self.check_in).days

    # ── Status transitions ────────────────────────────────────────────────────

    def confirm(self):
        if self.status != self.STATUS_PENDING:
            raise ValueError("Only pending bookings can be confirmed.")
        self.status = self.STATUS_CONFIRMED

    def cancel(self):
        if self.status == self.STATUS_CANCELLED:
            raise ValueError("Booking is already cancelled.")
        self.status = self.STATUS_CANCELLED

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
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
