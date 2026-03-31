from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from marketplace_andes.users.dependencies import UserRepositoryDep
from marketplace_andes.db.dependencies import SessionDep

from .service import AuthService
from .schemas import LoggedUser
from .user.dependencies import AuthUserRepositoryDep
from .session.dependencies import AuthSessionRepositoryDep
from .jwt.dependencies import JWTServiceDep
from .password.dependencies import PasswordHasherDep
from .exceptions import InternalAuthError

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login", scheme_name="JWT", refreshUrl="/auth/refresh"
)


TokenDep = Annotated[str, Depends(oauth2_scheme)]

AuthFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]


def get_auth_service(
    session: SessionDep,
    jwt_service: JWTServiceDep,
    password_hasher: PasswordHasherDep,
    auth_user_repo: AuthUserRepositoryDep,
    auth_session_repo: AuthSessionRepositoryDep,
    user_repo: UserRepositoryDep,
) -> AuthService:
    return AuthService(
        session,
        jwt_service,
        password_hasher,
        auth_user_repo,
        auth_session_repo,
        user_repo,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_current_user(
    token: TokenDep,
    auth_service: AuthServiceDep,
) -> LoggedUser:
    try:
        return auth_service.retrieve_user_session(token)
    except InternalAuthError as exc:
        raise HTTPException(
            status_code=status.INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc


CurrentUserDep = Annotated[LoggedUser, Depends(get_current_user)]
