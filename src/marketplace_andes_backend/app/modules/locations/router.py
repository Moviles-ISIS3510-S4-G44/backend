from typing import Annotated

from fastapi import APIRouter, Depends

from ...db.session import SessionDep
from .repository import LocationRepository
from .schemas import LocationCreate, LocationResponse
from .service import LocationService

router = APIRouter(prefix="/locations", tags=["locations"])


def get_location_service(session: SessionDep) -> LocationService:
    repository = LocationRepository(session)
    return LocationService(repository)


LocationServiceDep = Annotated[LocationService, Depends(get_location_service)]


@router.post("", response_model=LocationResponse)
def create_location(
    service: LocationServiceDep,
    location_create: LocationCreate,
) -> LocationResponse:
    return service.create_location(location_create)


@router.get("", response_model=list[LocationResponse])
def list_locations(service: LocationServiceDep) -> list[LocationResponse]:
    return service.get_locations()
