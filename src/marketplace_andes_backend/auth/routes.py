from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from .dependencies import AuthServiceDep, CurrentUserDep
from .schemas import CurrentUserResponse, SignupRequest, TokenResponse
from .service import DuplicateEmailError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, auth_service: AuthServiceDep) -> CurrentUserResponse:
    try:
        user = auth_service.signup(
            name=payload.name,
            email=payload.email,
            password=payload.password,
            university_id=payload.university_id,
            program_id=payload.program_id,
            is_verified=payload.is_verified,
            student_code=payload.student_code,
        )
    except DuplicateEmailError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        ) from exc

    return CurrentUserResponse.model_validate(user)


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> TokenResponse:
    try:
        access_token = auth_service.authenticate(
            email=form_data.username,
            password=form_data.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/me")
def read_current_user(current_user: CurrentUserDep) -> CurrentUserResponse:
    return CurrentUserResponse.model_validate(current_user)
