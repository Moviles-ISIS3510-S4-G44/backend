from fastapi import APIRouter
from sqlmodel import delete

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.auth.session.models import AuthSession
from marketplace_andes.auth.schemas import LoggedUser
from marketplace_andes.db.dependencies import SessionDep

from .dependencies import UserRepositoryDep
from .schemas import DeleteAllUsersResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=LoggedUser)
async def me(current_user: CurrentUserDep) -> LoggedUser:
    return LoggedUser.model_validate(current_user)


@router.get("", response_model=list[LoggedUser])
async def get_all_users(
    user_repository: UserRepositoryDep,
    _current_user: CurrentUserDep,
) -> list[LoggedUser]:
    users = user_repository.get_all_users()
    return [LoggedUser.model_validate(user) for user in users]


@router.delete("")
async def delete_all_users(
    session: SessionDep,
    user_repository: UserRepositoryDep,
    _current_user: CurrentUserDep,
) -> DeleteAllUsersResponse:
    session.exec(delete(AuthSession))
    deleted_count = user_repository.delete_all_users()
    session.commit()
    return DeleteAllUsersResponse(deleted_count=deleted_count)
