from uuid import uuid4

from .models import Location
from .repository import LocationRepository
from .schemas import LocationCreate, LocationResponse


class LocationService:
    def __init__(self, repository: LocationRepository):
        self.repository = repository

    def create_location(self, location_create: LocationCreate) -> LocationResponse:
        location = Location(id=uuid4(), name=location_create.name)
        created_location = self.repository.create_location(location)
        return LocationResponse.model_validate(created_location)
