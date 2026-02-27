import uuid
from datetime import datetime

class BaseModel:
    def __init__(self):
        # Génère un identifiant unique universel (UUID) sous forme de chaîne de caractères
        self.id = str(uuid.uuid4()) 
        
        # Enregistre la date et l'heure exactes de la création
        self.created_at = datetime.now() 
        
        # Au moment de la création, la date de mise à jour est la même que la création
        self.updated_at = datetime.now() 

    def update(self, data):
        """
        Met à jour les attributs de l'objet basés sur le dictionnaire 'data'
        et actualise la date de modification 'updated_at'.
        """
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # On actualise la date de mise à jour
        self.updated_at = datetime.now()