from fastapi import APIRouter

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.auth.schemas import LoggedUser


router = APIRouter(prefix="/user", tags=["users"])


@router.get("/me", response_model=LoggedUser)
async def me(current_user: CurrentUserDep) -> LoggedUser:
    return LoggedUser.model_validate(current_user)
