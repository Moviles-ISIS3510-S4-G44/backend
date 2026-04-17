from fastapi import APIRouter

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.auth.schemas import LoggedUser
from marketplace_andes.db.dependencies import SessionDep

from .dependencies import UserRepositoryDep
from .schemas import DeleteAllUsersResponse


router = APIRouter(prefix="/user", tags=["users"])


@router.get("/me")
async def me(current_user: CurrentUserDep) -> LoggedUser:
    return current_user


@router.delete("")
async def delete_all_users(
    session: SessionDep,
    user_repository: UserRepositoryDep,
    _: CurrentUserDep,
) -> DeleteAllUsersResponse:
    deleted_count = user_repository.delete_all_users()
    session.commit()
    return DeleteAllUsersResponse(deleted_count=deleted_count)
