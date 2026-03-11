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

    def __init__(self, place_id: str, user_id: str,
                 check_in: str, check_out: str,
                 guests: int = 1):
        super().__init__()

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

    def to_dict(self):
        booking_dict = super().to_dict()  # Start with base attributes (id, created_at, updated_at)
        booking_dict['place_id'] = self.place_id
        booking_dict['user_id'] = self.user_id
        booking_dict['check_in'] = self.check_in.isoformat()
        booking_dict['check_out'] = self.check_out.isoformat()
        booking_dict['nights'] = self.nights
        booking_dict['guests'] = self.guests
        booking_dict['status'] = self.status
        return booking_dict
