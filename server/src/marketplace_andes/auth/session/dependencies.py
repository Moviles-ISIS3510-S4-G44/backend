from typing import Annotated

from fastapi import Depends

from marketplace_andes.db.dependencies import SessionDep

from .repository import AuthSessionRepository


def get_auth_session_repository(session: SessionDep) -> AuthSessionRepository:
    return AuthSessionRepository(session)


AuthSessionRepositoryDep = Annotated[
    AuthSessionRepository, Depends(get_auth_session_repository)
]
