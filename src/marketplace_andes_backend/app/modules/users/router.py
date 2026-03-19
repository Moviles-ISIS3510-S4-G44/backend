from typing import Annotated

from fastapi import APIRouter, Depends

from ...db.session import SessionDep
from .repository import UserRepository
from .schemas import UserCreate, UserResponse
from .service import UserService

router = APIRouter(prefix="/users", tags=["users"])


def get_user_service(session: SessionDep) -> UserService:
    repository = UserRepository(session)
    return UserService(repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]


@router.post("", response_model=UserResponse)
def create_user(service: UserServiceDep, user_create: UserCreate) -> UserResponse:
    return service.create_user(user_create)


@router.get("", response_model=list[UserResponse])
def list_users(service: UserServiceDep) -> list[UserResponse]:
    return service.get_users()
