from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path

from src.marketplace_andes_backend.db import SessionDep

from .schemas import InteractionRegisterRequest, InteractionResponse
from .service import InteractionService

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("")
async def register_interaction(
    payload: InteractionRegisterRequest,
    session: SessionDep,
) -> InteractionResponse:
    service = InteractionService(session)

    if not service.user_exists(payload.user_id):
        raise HTTPException(status_code=404, detail="User not found")

    if not service.listing_exists(payload.listing_id):
        raise HTTPException(status_code=404, detail="Listing not found")

    interaction = service.register_interaction(
        user_id=payload.user_id,
        listing_id=payload.listing_id,
    )
    return InteractionResponse.model_validate(interaction)


@router.get("/users/{user_id}/top")
async def get_top_user_interactions(
    user_id: Annotated[UUID, Path()],
    session: SessionDep,
) -> list[InteractionResponse]:
    service = InteractionService(session)

    if not service.user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")

    interactions = service.get_top_interactions_by_user(user_id)
    return [InteractionResponse.model_validate(item) for item in interactions]
