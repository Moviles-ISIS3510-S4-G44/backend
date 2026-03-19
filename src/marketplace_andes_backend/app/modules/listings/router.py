from typing import Annotated

from fastapi import APIRouter, Depends

from marketplace_andes_backend.app.modules.listings.models import Listing

from ...db.session import SessionDep
from .repository import ListingRepository
from .schemas import ListingCreate, ListingCreateResponse, ListingListResponse
from .service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


def get_listing_service(session: SessionDep) -> ListingService:
    repository = ListingRepository(session)
    return ListingService(repository)


ListingServiceDep = Annotated[ListingService, Depends(get_listing_service)]


@router.get("", response_model=ListingListResponse)
def list_listings(service: ListingServiceDep) -> ListingListResponse:
    return service.get_listings()


@router.post("", response_model=ListingCreateResponse)
def create_listing(
    data: ListingCreate,
    service: ListingServiceDep,
) -> ListingCreateResponse:
    return service.create_listing(data)
