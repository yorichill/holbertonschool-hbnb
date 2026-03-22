from app.models.base_model import BaseModel
from app import bcrypt, db
import re


class User(BaseModel):
    __tablename__ = 'users'

    # Colonnes SQLAlchemy
    # Les colonnes avec @property utilisent le nom privé (_first_name, etc.)
    _first_name = db.Column('first_name', db.String(50), nullable=False)
    _last_name = db.Column('last_name', db.String(50), nullable=False)
    _email = db.Column('email', db.String(120), nullable=False, unique=True)
    _password = db.Column('password', db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
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
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, value):
        if not isinstance(value, str):
            raise TypeError("Password must be a string")
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not value.startswith(("$2a$", "$2b$", "$2y$")):
            self._password = bcrypt.generate_password_hash(value).decode("utf-8")
        else:
            self._password = value

    def hash_password(self, password):
        self.password = password

    def verify_password(self, password):
        return bcrypt.check_password_hash(self._password, password)

    # ===================== SERIALIZATION =====================

    def to_dict(self):
        user_dict = super().to_dict()
        user_dict["first_name"] = self.first_name
        user_dict["last_name"] = self.last_name
        user_dict["email"] = self.email
        user_dict["is_admin"] = self.is_admin
        return user_dict
