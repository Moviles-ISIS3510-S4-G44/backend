from .repository import LocationRepository


class LocationService:
    def __init__(self, repository: LocationRepository):
        self.repository = repository

