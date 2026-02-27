from app.models.base_model import BaseModel

class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()
        self.text = text
        self.rating = rating
        self.place = place # Instance de Place
        self.user = user   # Instance de User
        self.validate()

    def validate(self):
        if not self.text:
            raise ValueError("Le texte de l'avis est obligatoire.")
        if not isinstance(self.rating, int) or not (1 <= self.rating <= 5):
            raise ValueError("La note doit être un entier compris entre 1 et 5.")