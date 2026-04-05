import re
from app.models.base_model import BaseModel


class User(BaseModel):
    """
    Represents an application user.

    Accepts kwargs so it can be built directly from a request dict:
        user = User(**user_data)
    or via the factory:
        user = User.from_dict(user_data)
    """

    def __init__(self, first_name: str = '', last_name: str = '',
                 email: str = '', is_admin: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.first_name = self._validate_name(first_name, 'first_name')
        self.last_name  = self._validate_name(last_name,  'last_name')
        self.email      = self._validate_email(email)
        self.is_admin   = bool(is_admin)

    # ── Validators ────────────────────────────────────────────────────────────

    @staticmethod
    def _validate_name(value: str, field: str) -> str:
        if not value or len(value) > 50:
            raise ValueError(f"{field} must be between 1 and 50 characters.")
        return value

    @staticmethod
    def _validate_email(email: str) -> str:
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            raise ValueError("Invalid email address.")
        return email

    # ── Serialisation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        base = super().to_dict()
        base.update({
            'first_name': self.first_name,
            'last_name':  self.last_name,
            'email':      self.email,
            'is_admin':   self.is_admin,
        })
        return base
