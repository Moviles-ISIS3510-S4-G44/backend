from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.db.dependencies import SessionDep

from .schemas import FavoriteCreateRequest, FavoritesListResponse
from .service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("")
async def list_my_favorites(
    session: SessionDep,
    current_user: CurrentUserDep,
) -> FavoritesListResponse:
    service = FavoriteService(session)
    ids = service.list_favorite_listing_ids(current_user.id)
    return FavoritesListResponse(listing_ids=ids)


@router.post("", status_code=201)
async def add_favorite(
    payload: FavoriteCreateRequest,
    session: SessionDep,
    current_user: CurrentUserDep,
) -> None:
    service = FavoriteService(session)
    if not service.listing_exists(payload.listing_id):
        raise HTTPException(status_code=404, detail="Listing not found")
    service.add_favorite(current_user.id, payload.listing_id)


@router.delete("/{listing_id}", status_code=204)
async def remove_favorite(
    listing_id: Annotated[UUID, Path()],
    session: SessionDep,
    current_user: CurrentUserDep,
) -> None:
    service = FavoriteService(session)
    service.remove_favorite(current_user.id, listing_id)
