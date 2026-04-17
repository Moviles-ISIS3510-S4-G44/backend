from fastapi import APIRouter, HTTPException, status

from marketplace_andes.ip.dependencies import AnonIpDep

from .dependencies import AuthFormDep, AuthServiceDep
from .exceptions import (
    AuthSessionNotFoundError,
    DuplicateUserError,
    ExpiredAuthSessionError,
    InactiveAuthSessionError,
    InternalAuthError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from .schemas import (
    LoginResponse,
    LogoutRequest,
    RefreshTokenRequest,
    RegisterUserRequest,
    RegisterUserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    form_data: AuthFormDep, auth_service: AuthServiceDep, anon_ip: AnonIpDep
) -> LoginResponse:
    try:
        return auth_service.authenticate_user(
            form_data.username, form_data.password, anon_ip
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except InternalAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc


@router.post("/logout")
async def logout(
    logout_request: LogoutRequest, auth_service: AuthServiceDep, anon_ip: AnonIpDep
):
    try:
        auth_service.logout_user(
            logout_request.session_id, logout_request.refresh_token, anon_ip
        )
    except AuthSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (InactiveAuthSessionError, ExpiredAuthSessionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user: RegisterUserRequest, auth_service: AuthServiceDep, anon_ip: AnonIpDep
) -> RegisterUserResponse:
    try:
        return RegisterUserResponse(
            user_id=auth_service.register_user(user.username, user.password, anon_ip)
        )
    except DuplicateUserError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
)
async def refresh(
    request: RefreshTokenRequest, auth_service: AuthServiceDep, anon_ip: AnonIpDep
) -> LoginResponse:
    try:
        return auth_service.refresh_access_token(request.refresh_token, anon_ip)
    except AuthSessionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    except (InactiveAuthSessionError, ExpiredAuthSessionError) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    except InvalidRefreshTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    except InternalAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc
