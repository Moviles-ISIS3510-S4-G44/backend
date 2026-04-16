from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid7

from fastapi import APIRouter, HTTPException, Path

from marketplace_andes.db.dependencies import SessionDep

from .models import Listing
from .schemas import (
    ListingCreateRequest,
    ListingResponse,
    StatusHistoryResponse,
)
from .service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("")
async def create_listing(
    payload: ListingCreateRequest,
    session: SessionDep,
) -> ListingResponse:
    service = ListingService(session)
    if not service.seller_exists(payload.seller_id):
        raise HTTPException(status_code=404, detail="Seller not found")
    if not service.category_exists(payload.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    now = datetime.now(UTC)
    listing = Listing(
        id=uuid7(),
        seller_id=payload.seller_id,
        category_id=payload.category_id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        condition=payload.condition,
        images=payload.images,
        status="draft",
        location=payload.location,
        created_at=now,
        updated_at=now,
    )
    listing = service.create(listing)
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


@router.patch("/{listing_id}/status")
async def update_listing_status(
    listing_id: Annotated[UUID, Path()],
    new_status: str,
    session: SessionDep,
) -> ListingResponse:
    service = ListingService(session)
    listing = service.update_status(listing_id, new_status)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return ListingResponse.model_validate(listing)


@router.get("/{listing_id}/history")
async def get_listing_history(
    listing_id: Annotated[UUID, Path()],
    session: SessionDep,
) -> list[StatusHistoryResponse]:
    service = ListingService(session)
    history = service.get_history(listing_id)
    return [StatusHistoryResponse.model_validate(h) for h in history]
