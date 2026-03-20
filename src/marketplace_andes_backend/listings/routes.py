from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from src.marketplace_andes_backend.db import SessionDep

from .models import Listing
from .schemas import ListingCreateRequest, ListingResponse
from .service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("")
async def create_listing(
    payload: ListingCreateRequest,
    session: SessionDep,
) -> ListingResponse:
    service = ListingService(session)
    if not service.user_exists(payload.seller_id):
        raise HTTPException(status_code=404, detail="Seller not found")
    if not service.category_exists(payload.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    listing = service.create(Listing(**payload.model_dump()))
    return ListingResponse.model_validate(listing)


@router.get("")
async def list_listings(session: SessionDep) -> list[ListingResponse]:
    service = ListingService(session)
    listings = service.list_all()
    return [ListingResponse.model_validate(listing) for listing in listings]


@router.get("/{listing_id}")
async def get_listing(
    listing_id: Annotated[UUID, Path()],
    session: SessionDep,
) -> ListingResponse:
    service = ListingService(session)
    listing = service.get_by_id(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingResponse.model_validate(listing)
