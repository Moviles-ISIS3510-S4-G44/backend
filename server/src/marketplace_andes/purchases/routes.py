from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.db.dependencies import SessionDep

from .schemas import PurchaseCreateRequest, PurchaseResponse, RateSellerRequest
from .service import PurchaseService

router = APIRouter(prefix="/purchases", tags=["purchases"])


@router.post("", status_code=201)
async def create_purchase(
    payload: PurchaseCreateRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> PurchaseResponse:
    service = PurchaseService(session)

    listing = service.get_listing(payload.listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")

    if listing.status != "published":
        raise HTTPException(
            status_code=409,
            detail="Listing is not available for purchase",
        )

    if listing.seller_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot purchase your own listing",
        )

    if service.already_purchased(payload.listing_id):
        raise HTTPException(
            status_code=409,
            detail="Listing has already been purchased",
        )

    purchase = service.create_purchase(
        buyer_id=current_user.id,
        listing_id=payload.listing_id,
    )
    return PurchaseResponse.model_validate(purchase)


@router.get("/me")
async def get_my_purchases(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[PurchaseResponse]:
    service = PurchaseService(session)
    purchases = service.get_purchases_by_buyer(current_user.id)
    return [PurchaseResponse.model_validate(p) for p in purchases]


@router.get("/sold")
async def get_my_sales(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> list[PurchaseResponse]:
    service = PurchaseService(session)
    purchases = service.get_purchases_as_seller(current_user.id)
    return [PurchaseResponse.model_validate(p) for p in purchases]


@router.patch("/{purchase_id}/rate-seller")
async def rate_seller(
    purchase_id: Annotated[UUID, Path()],
    payload: RateSellerRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> PurchaseResponse:
    service = PurchaseService(session)
    purchase = service.rate_seller(
        purchase_id=purchase_id,
        buyer_id=current_user.id,
        rating=payload.rating,
    )
    if purchase is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase not found or does not belong to you",
        )
    return PurchaseResponse.model_validate(purchase)
