from app.models.base_model import BaseModel

class Amenity(BaseModel):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.validate()

    def validate(self):
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Le nom de l'équipement ne peut pas être vide.")