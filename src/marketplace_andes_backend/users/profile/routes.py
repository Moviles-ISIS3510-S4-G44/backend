from fastapi import APIRouter, HTTPException

from src.marketplace_andes_backend.db import SessionDep

from .schemas import UserProfileResponse
from .service import UserProfileService

router = APIRouter(prefix="/profile", tags=["users"])


@router.get("/{user_id}")
async def get_user_profile(
    user_id: int,
    session: SessionDep,
) -> UserProfileResponse:
    service = UserProfileService(session)
    user = service.get_info(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfileResponse.model_validate(user)
