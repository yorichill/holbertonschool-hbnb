class Repository:
    pass # Interface de base

class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}
    # ... les autres méthodes
