import re
from app.models.base_model import BaseModel

class User(BaseModel):
    def __init__(self, first_name, last_name, email, is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.validate()

    def validate(self):
        if not self.first_name or not self.last_name:
            raise ValueError("Le prénom et le nom sont obligatoires.")
        if not self.email or not re.match(r"[^@]+@[^@]+\.[^@]+", self.email):
            raise ValueError("Format d'email invalide.")