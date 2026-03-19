from datetime import UTC, datetime, timedelta
from uuid import UUID

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as JWTInvalidTokenError
from sqlmodel import Session, select

from ..config import get_settings
from ..users.models import User
from .models import UserAuth

PWD_HASHER = PasswordHasher()


class DuplicateEmailError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.settings = get_settings()

    def hash_password(self, password: str) -> str:
        return PWD_HASHER.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            return PWD_HASHER.verify(hashed_password, password)
        except (InvalidHashError, VerificationError):
            return False

    def create_access_token(self, user: User) -> str:
        expires_at = datetime.now(UTC) + timedelta(
            minutes=self.settings.jwt_access_token_expire_minutes
        )
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "exp": expires_at,
        }
        return jwt.encode(
            payload,
            self.settings.jwt_secret_key,
            algorithm=self.settings.jwt_algorithm,
        )

    def decode_access_token(self, token: str) -> dict[str, str]:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret_key,
                algorithms=[self.settings.jwt_algorithm],
            )
        except (ExpiredSignatureError, JWTInvalidTokenError) as exc:
            raise InvalidTokenError() from exc

        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise InvalidTokenError()

        return payload

    def signup(self, name: str, email: str, password: str) -> User:
        existing_user = self.session.exec(select(User).where(User.email == email)).first()
        if existing_user is not None:
            raise DuplicateEmailError()

        user = User(name=name, email=email)
        self.session.add(user)
        self.session.flush()
        if user.id is None:
            raise InvalidTokenError()

        user_auth = UserAuth(
            id=user.id,
            user_id=user.id,
            hashed_password=self.hash_password(password),
        )
        self.session.add(user_auth)
        self.session.commit()
        self.session.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> str:
        user = self.session.exec(select(User).where(User.email == email)).first()
        if user is None:
            raise InvalidCredentialsError()

        user_auth = self.session.exec(
            select(UserAuth).where(UserAuth.user_id == user.id)
        ).first()
        if user_auth is None or not self.verify_password(password, user_auth.hashed_password):
            raise InvalidCredentialsError()

        return self.create_access_token(user)

    def get_user_by_token(self, token: str) -> User:
        payload = self.decode_access_token(token)
        try:
            user_id = UUID(payload["sub"])
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidTokenError() from exc

        user = self.session.exec(select(User).where(User.id == user_id)).first()
        if user is None:
            raise InvalidTokenError()

        return user
