class Repository:
    pass

class InMemoryRepository(Repository):
    def __init__(self):
        self._storage = {}
