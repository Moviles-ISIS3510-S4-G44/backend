from typing import Annotated

from fastapi import Depends

from marketplace_andes.db.dependencies import SessionDep

from .repository import AuthUserRepository


def get_auth_user_repository(session: SessionDep) -> AuthUserRepository:
    return AuthUserRepository(session)


AuthUserRepositoryDep = Annotated[AuthUserRepository, Depends(get_auth_user_repository)]
