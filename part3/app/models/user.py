import re
from app.models.base_model import BaseModel
# On importe notre outil bcrypt qu'on a créé dans __init__.py
from app import bcrypt 

class User(BaseModel):
    def __init__(self, first_name, last_name, email, password="", is_admin=False):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_admin = is_admin
        self.password = password # Contiendra le mot de passe haché

    def hash_password(self, password):
        """Hache le mot de passe avant de le stocker."""
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        """Vérifie si le mot de passe fourni correspond au hash."""
        return bcrypt.check_password_hash(self.password, password)

    def to_dict(self):
        """Transforme l'objet en dictionnaire, sans révéler le mot de passe."""
        user_dict = super().to_dict()
        user_dict['first_name'] = self.first_name
        user_dict['last_name'] = self.last_name
        user_dict['email'] = self.email
        user_dict['is_admin'] = self.is_admin
        
        # On supprime le mot de passe pour qu'il n'apparaisse JAMAIS dans les GET
        if 'password' in user_dict:
            del user_dict['password']
            
        return user_dict