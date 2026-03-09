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
        self.password = password  # This will be hashed by the setter
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
        """Get the hashed password (for internal use only)."""
        return self._password

    @password.setter
    def password(self, value):
        """Set the password, hashing it if it's not already hashed."""
        if not value or len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        # Si la valeur ne semble pas être un hash bcrypt (commence par $2b$), on la hash
        if not value.startswith('$2b$'):
            self._password = bcrypt.generate_password_hash(value).decode('utf-8')
        else:
            self._password = value

    def verify_password(self, password):
        """Verify a plaintext password against the stored hashed password."""
        return bcrypt.check_password_hash(self._password, password)

    # ===================== SERIALIZATION =====================

    def to_dict(self):
        """
        Convert User to dictionary.
        Excludes password for security reasons.
        """
        user_dict = super().to_dict() # Start with base attributes (id, created_at, updated_at)
        user_dict["first_name"] = self.first_name
        user_dict["last_name"] = self.last_name
        user_dict["email"] = self.email
        user_dict["is_admin"] = self.is_admin
        return user_dict

    # ===================== PLACEHOLDERS =====================

    def register(self):
        """Register the user in the database (to be implemented in Part3)"""
        pass

    def authenticate(self, password):
        """Authenticate the user with the provided password"""
        return self.verify_password(password)

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
