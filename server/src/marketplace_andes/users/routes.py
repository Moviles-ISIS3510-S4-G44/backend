from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Path, status
from sqlmodel import delete

from marketplace_andes.auth.dependencies import CurrentUserDep
from marketplace_andes.auth.session.models import AuthSession
from marketplace_andes.auth.schemas import LoggedUser, PublicUser
from marketplace_andes.db.dependencies import SessionDep
from marketplace_andes.profile_visits.schemas import ProfileVisitCreatedResponse
from marketplace_andes.profile_visits.service import ProfileVisitService

from .dependencies import UserRepositoryDep
from .schemas import DeleteAllUsersResponse


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=LoggedUser)
async def me(current_user: CurrentUserDep) -> LoggedUser:
    return LoggedUser.model_validate(current_user)


@router.get("/{user_id}", response_model=PublicUser)
async def get_user_profile_by_id(
    user_id: Annotated[UUID, Path()],
    user_repository: UserRepositoryDep,
    _current_user: CurrentUserDep,
) -> PublicUser:
    user = user_repository.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    profile = user_repository.get_user_profile_by_id(user_id)
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return PublicUser.model_validate(profile)


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


@router.post(
    "/{visited_user_id}/profile-visits",
    response_model=ProfileVisitCreatedResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_profile_visit(
    visited_user_id: Annotated[UUID, Path()],
    session: SessionDep,
    current_user: CurrentUserDep,
) -> ProfileVisitCreatedResponse:
    service = ProfileVisitService(session)
    try:
        event = service.register_visit(
            visitor_user_id=current_user.id,
            visited_user_id=visited_user_id,
        )
    except ValueError as exc:
        if str(exc) == "cannot_visit_self":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot record a visit to your own profile",
            ) from exc
        raise
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return ProfileVisitCreatedResponse.model_validate(event)
