import secrets
from datetime import UTC, datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import or_
from sqlmodel import Session, select

from backend.auth.models import RefreshToken, User
from backend.auth.schemas import TokenPayload, UserCreate
from backend.config import get_settings

pwd_context = CryptContext(schemes=["argon2"])


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> TokenPayload:
    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        subject = payload.get("sub")
        if not subject:
            raise _credentials_exception()
        return TokenPayload(sub=subject, exp=payload["exp"])
    except jwt.ExpiredSignatureError as exc:
        raise _credentials_exception(detail="Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise _credentials_exception() from exc


def get_user_by_identifier(session: Session, identifier: str) -> User | None:
    statement = select(User).where(
        or_(User.email == identifier, User.username == identifier)
    )
    return session.exec(statement).first()


def register_user(session: Session, data: UserCreate) -> User:
    existing = session.exec(
        select(User).where(or_(User.email == data.email, User.username == data.username))
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )

    user = User(
        email=data.email,
        username=data.username,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, identifier: str, password: str) -> User:
    user = get_user_by_identifier(session, identifier)

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


def _credentials_exception(detail: str = "Could not validate credentials") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def create_refresh_token(session: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(UTC) + timedelta(days=get_settings().refresh_token_expire_days)
    
    refresh_token = RefreshToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    
    session.add(refresh_token)
    session.commit()
    session.refresh(refresh_token)
    
    return token


def validate_refresh_token(session: Session, token: str) -> RefreshToken:
    statement = select(RefreshToken).where(
        RefreshToken.token == token,
        RefreshToken.is_revoked == False
    )
    refresh_token = session.exec(statement).first()
    
    if not refresh_token:
        raise _credentials_exception("Invalid refresh token")
    
    if refresh_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise _credentials_exception("Refresh token expired")
    
    return refresh_token


def revoke_refresh_token(session: Session, token: str) -> None:
    statement = select(RefreshToken).where(RefreshToken.token == token)
    refresh_token = session.exec(statement).first()
    
    if refresh_token:
        refresh_token.is_revoked = True
        session.commit()


def revoke_user_refresh_tokens(session: Session, user_id: int) -> None:
    statement = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.is_revoked == False
    )
    refresh_tokens = session.exec(statement).all()
    
    for token in refresh_tokens:
        token.is_revoked = True
    
    session.commit()
