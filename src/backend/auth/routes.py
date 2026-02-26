from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from backend.auth.dependencies import get_current_active_user
from backend.auth.models import User
from backend.auth.schemas import RefreshTokenRequest, Token, UserCreate, UserLogin, UserRead
from backend.auth.service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    register_user,
    revoke_refresh_token,
    validate_refresh_token,
)
from backend.config import get_settings
from backend.database import get_session

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, session: Session = Depends(get_session)) -> User:
    return register_user(session, payload)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, session: Session = Depends(get_session)) -> Token:
    user = authenticate_user(session, payload.identifier, payload.password)
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(session, user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=get_settings().access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_active_user)) -> User:
    return current_user


@router.post("/refresh", response_model=Token)
def refresh(payload: RefreshTokenRequest, session: Session = Depends(get_session)) -> Token:
    refresh_token_obj = validate_refresh_token(session, payload.refresh_token)
    
    access_token = create_access_token(str(refresh_token_obj.user_id))
    
    revoke_refresh_token(session, payload.refresh_token)
    new_refresh_token = create_refresh_token(session, refresh_token_obj.user_id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=get_settings().access_token_expire_minutes * 60,
    )
