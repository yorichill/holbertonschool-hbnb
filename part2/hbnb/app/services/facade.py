from app.persistence.repository import InMemoryRepository

class HBnBFacade:
    def __init__(self):
        # On initialise les dépôts pour chaque entité
        self.user_repo = InMemoryRepository()
        self.place_repo = InMemoryRepository()
        self.review_repo = InMemoryRepository()
        self.amenity_repo = InMemoryRepository()

    # Placeholder : Logique pour créer un utilisateur
    def create_user(self, user_data):
        pass

    # Placeholder : Logique pour récupérer un lieu
    def get_place(self, place_id):
        pass