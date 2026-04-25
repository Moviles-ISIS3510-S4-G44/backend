from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID, uuid7

from fastapi import APIRouter, HTTPException, Path, Query

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.db.dependencies import SessionDep

from .enums import ListingCondition
from .models import Listing
from .schemas import (
    DeleteAllListingsResponse,
    ListingCreateRequest,
    ListingResponse,
    ListingUpdateRequest,
    StatusHistoryResponse,
)
from .service import ListingService

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("", status_code=201)
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
async def list_listings(
    session: SessionDep,
    q: str | None = Query(default=None),
    category_id: UUID | None = Query(default=None),
    condition: ListingCondition | None = Query(default=None),
    min_price: int | None = Query(default=None),
    max_price: int | None = Query(default=None),
    location: str | None = Query(default=None),
    status: str | None = Query(default=None),
) -> list[ListingResponse]:
    service = ListingService(session)
    listings = service.search(
        q=q,
        category_id=category_id,
        condition=condition,
        min_price=min_price,
        max_price=max_price,
        location=location,
        status=status,
    )
    return [ListingResponse.model_validate(listing) for listing in listings]


@router.get("/me")
async def get_my_listings(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[ListingResponse]:
    service = ListingService(session)
    listings = service.get_by_seller(current_user.id)
    return [ListingResponse.model_validate(listing) for listing in listings]


@router.delete("")
async def delete_all_listings(session: SessionDep) -> DeleteAllListingsResponse:
    service = ListingService(session)
    deleted_count = service.delete_all()
    return DeleteAllListingsResponse(deleted_count=deleted_count)


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


@router.patch("/{listing_id}", status_code=200)
async def update_listing(
    listing_id: Annotated[UUID, Path()],
    payload: ListingUpdateRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ListingResponse:
    service = ListingService(session)

    listing = service.get_by_id(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.seller_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only the seller can edit this listing")
    if listing.status == "sold":
        raise HTTPException(status_code=409, detail="Sold listings cannot be edited")
    if payload.category_id is not None and not service.category_exists(payload.category_id):
        raise HTTPException(status_code=404, detail="Category not found")

    updated = service.update_listing(listing_id, payload)
    return ListingResponse.model_validate(updated)


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
