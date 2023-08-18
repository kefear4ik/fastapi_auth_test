__all__ = ('BaseService',)


class BaseService:
    def __init__(self, storage):
        self.storage = storage
