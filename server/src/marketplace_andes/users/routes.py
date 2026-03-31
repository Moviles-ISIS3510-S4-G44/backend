from fastapi import APIRouter

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.auth.schemas import LoggedUser


router = APIRouter(prefix="/user", tags=["users"])


@router.get("/me")
async def me(current_user: CurrentUserDep) -> LoggedUser:
    return current_user
