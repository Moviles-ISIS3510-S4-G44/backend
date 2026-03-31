from typing import Annotated

from fastapi import Depends

from marketplace_andes.db.dependencies import SessionDep

from .repository import UserRepository


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
