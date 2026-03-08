from app.models import BaseModel
from app import bcrypt
import re


class User(BaseModel):
    """
    User model representing a user in the system.
    Can be a guest or a property owner.
    """

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        """
        Initialize User instance with provided attributes.
        """
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hash_password(password)
        self.is_admin = is_admin

    # ===================== FIRST NAME =====================

    @property
    def first_name(self):
        return self._first_name

    @first_name.setter
    def first_name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("First name is required and must be a string")

        value = value.strip()
        if not value:
            raise ValueError("First name cannot be empty")

        self._first_name = value

    # ===================== LAST NAME =====================

    @property
    def last_name(self):
        return self._last_name

    @last_name.setter
    def last_name(self, value):
        if not value or not isinstance(value, str):
            raise ValueError("Last name is required and must be a string")

        value = value.strip()
        if not value:
            raise ValueError("Last name cannot be empty")

        self._last_name = value

    # ===================== EMAIL =====================

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = self._validate_email(value)

    @staticmethod
    def _validate_email(email):
        """
        Validate email format.
        """
        if not email or not isinstance(email, str):
            raise ValueError("Email is required and must be a string")

        email = email.strip().lower()

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.fullmatch(email_regex, email):
            raise ValueError("Invalid email format")

        return email

    # ===================== PASSWORD =====================

    @property
    def password(self):
        """Getter for password (returns None for security reasons)"""
        return None

    @password.setter
    def hash_password(self, password):
        """Hashes the password before storing it."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Verifies if the provided password matches the hashed password."""
        return bcrypt.check_password_hash(self.password, password)

    def validate_password(self):
        """
        Validate password strength.
        """
        return len(self._password) >= 8

    # ===================== SERIALIZATION =====================

    def to_dict(self):
        """
        Convert User to dictionary.
        Excludes password for security reasons.
        """
        user_dict = super().to_dict()
        user_dict["first_name"] = self.first_name
        user_dict["last_name"] = self.last_name
        user_dict["email"] = self.email
        user_dict["is_admin"] = self.is_admin

        # sécurité
        user_dict.pop("_password", None)
        return user_dict

    # ===================== PLACEHOLDERS =====================

    def register(self):
        """Register the user in the database (to be implemented in Part3)"""
        pass

    def authenticate(self, password):
        """
        Authenticate user with password.
        """
        return self._password == password

    def add_place(self, title, description, price, latitude, longitude):
        """Add a place for the user (to be implemented in Part3)"""
        pass

    def has_reserved(self, place):
        """Check if user has reserved a place (to be implemented in Part3)"""
        pass

    def add_review(self, text, rating):
        """Add a review for a place (to be implemented in Part3)"""
        pass

    def add_amenity(self, name, description):
        """Add an amenity for the user (to be implemented in Part3)"""
        pass
