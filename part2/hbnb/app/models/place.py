from app.models.base_model import BaseModel

class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner):
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner # Instance de User ADMIN
        self.reviews = []  # Liste des avis liés à cette place
        self.amenities = [] # Liste des équipements (Amenity)
        self.validate()

    def validate(self):
        if not self.title:
            raise ValueError("Le titre est obligatoire.")
        if self.price < 0:
            raise ValueError("Le prix doit être une valeur positive.")
        if not (-90.0 <= self.latitude <= 90.0) or not (-180.0 <= self.longitude <= 180.0):
            raise ValueError("Les coordonnées GPS (latitude/longitude) sont invalides.")
            
    def add_review(self, review):
        self.reviews.append(review)

    def add_amenity(self, amenity):
        self.amenities.append(amenity)