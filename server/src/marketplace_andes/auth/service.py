import logging
from uuid import UUID
from datetime import UTC, datetime

from sqlmodel import Session

from marketplace_andes.users.repository import UserRepository

from .schemas import LoggedUser, LoginResponse
from .exceptions import (
    AuthSessionNotFoundError,
    DuplicateUserError,
    ExpiredAuthSessionError,
    InactiveAuthSessionError,
    InternalAuthError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from .user.repository import AuthUserRepository
from .session.repository import AuthSessionRepository
from .jwt.service import JWTService
from .password.interface import IPasswordHasher


logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        session: Session,
        jwt_service: JWTService,
        password_hasher: IPasswordHasher,
        auth_repository: AuthUserRepository,
        auth_session_repository: AuthSessionRepository,
        user_repository: UserRepository,
    ):
        self.__session = session
        self.__jwt_service = jwt_service
        self.__password_hasher = password_hasher
        self.__auth_repository = auth_repository
        self.__auth_session_repository = auth_session_repository
        self.__user_repository = user_repository
        self.__logger = logger.getChild(self.__class__.__name__)

    def authenticate_user(
        self, email: str, password: str, anon_ip: str
    ) -> LoginResponse:
        self.__logger.info(
            f"Authentication attempt for email: {email} at IP: {anon_ip}"
        )

        user_id = self.__user_repository.get_id_from_email(email)
        if not user_id:
            self.__logger.warning(
                f"Authentication attempted for unknown email: {email} at IP: {anon_ip}"
            )
            raise InvalidCredentialsError("Invalid email or password")

        hashed_password = self.__auth_repository.get_hashed_password(user_id)

        if not hashed_password:
            self.__logger.error(
                f"Authentication error: hashed password not found for email: {email} at IP: {anon_ip}"
            )
            raise InternalAuthError

        try:
            self.__password_hasher.verify(hashed_password, password)
        except Exception as e:
            self.__logger.warning(
                f"Authentication failed: invalid password for email: {email} at IP: {anon_ip}"
            )
            raise InvalidCredentialsError("Invalid email or password") from e

        refresh_token = self.__jwt_service.create_refresh_token()
        hash_token = self.__jwt_service.hash_token(refresh_token.token)

        auth_session = self.__auth_session_repository.create_session(
            user_id, hash_token, refresh_token.expires_at, anon_ip
        )
        session_id = auth_session.id
        self.__session.commit()

        self.__logger.info(
            f"Email: {email} authenticated successfully at IP: {anon_ip} and session_id: {session_id}"
        )
        return LoginResponse(
            session_id=session_id,
            access_token=self.__jwt_service.create_access_token(user_id),
            expires_in=self.__jwt_service.jwt_access_token_expire_minutes * 60,
            refresh_token=refresh_token.token,
            refresh_expires_in=self.__jwt_service.jwt_refresh_token_expire_minutes * 60,
        )

    def register_user(self, email: str, password: str, name: str, anon_ip: str) -> UUID:
        if self.__user_repository.get_id_from_email(email):
            self.__logger.warning(
                f"Registration attempted with existing email: {email} at IP: {anon_ip}"
            )
            raise DuplicateUserError("Email already exists")

        user = self.__user_repository.create_user(email)
        self.__session.flush()

        user_id = user.id

        self.__user_repository.create_user_profile(user_id, name)

        self.__auth_repository.create_auth_user(
            user_id, self.__password_hasher.hash(password)
        )

        self.__session.commit()

        self.__logger.info(
            f"User with email: {email} registered successfully with id: {user_id} at IP: {anon_ip}"
        )

        return user_id

    def logout_user(self, session_id: UUID, refresh_token: str, anon_ip: str) -> None:
        status = self.__auth_session_repository.get_session_status_by_id(session_id)
        if not status:
            self.__logger.warning(
                f"Logout attempted for session_id {session_id} with no active session at IP: {anon_ip}"
            )
            raise AuthSessionNotFoundError("Session not found")

        token_hash, expires_at, revoked_at = status
        if revoked_at is not None:
            self.__logger.warning(
                f"Logout attempted for session_id {session_id} which is already inactive at IP: {anon_ip}"
            )
            raise InactiveAuthSessionError("Session is already inactive")

        if datetime.now(UTC) > expires_at:
            self.__logger.warning(
                f"Logout attempted for expired session_id {session_id} at IP: {anon_ip}"
            )
            raise ExpiredAuthSessionError("Session has expired")

        if self.__jwt_service.hash_token(refresh_token) != token_hash:
            self.__logger.warning(
                f"Logout failed: invalid refresh token for session_id {session_id} at IP: {anon_ip}"
            )
            raise InvalidRefreshTokenError("Invalid refresh token")

        self.__auth_session_repository.revoke_session(session_id)
        self.__session.commit()
        self.__logger.info(
            f"Session_id {session_id} logged out successfully at IP: {anon_ip}"
        )

    def refresh_access_token(self, refresh_token: str, anon_ip: str) -> LoginResponse:
        token_hash = self.__jwt_service.hash_token(refresh_token)
        auth_session = self.__auth_session_repository.get_session_by_refresh_token_hash(
            token_hash
        )
        if not auth_session:
            self.__logger.warning(
                f"Refresh attempted with unknown refresh token at IP: {anon_ip}"
            )
            raise AuthSessionNotFoundError("Session not found")

        if auth_session.revoked_at is not None:
            self.__logger.warning(
                f"Refresh attempted for inactive session_id {auth_session.id} at IP: {anon_ip}"
            )
            raise InactiveAuthSessionError("Session is already inactive")

        if datetime.now(UTC) > auth_session.expires_at:
            self.__logger.warning(
                f"Refresh attempted for expired session_id {auth_session.id} at IP: {anon_ip}"
            )
            raise ExpiredAuthSessionError("Session has expired")

        self.__auth_session_repository.revoke_session(auth_session.id)

        new_access_token = self.__jwt_service.create_access_token(auth_session.user_id)
        new_refresh_token = self.__jwt_service.create_refresh_token()
        new_refresh_token_hash = self.__jwt_service.hash_token(new_refresh_token.token)

        new_auth_session = self.__auth_session_repository.create_session(
            auth_session.user_id,
            new_refresh_token_hash,
            new_refresh_token.expires_at,
            anon_ip,
        )
        user_id = auth_session.user_id
        session_id = new_auth_session.id
        self.__session.commit()

        self.__logger.info(
            f"Access token refreshed successfully for user_id {user_id} at IP: {anon_ip}"
        )

        return LoginResponse(
            session_id=session_id,
            access_token=new_access_token,
            expires_in=self.__jwt_service.jwt_access_token_expire_minutes * 60,
            refresh_token=new_refresh_token.token,
            refresh_expires_in=self.__jwt_service.jwt_refresh_token_expire_minutes * 60,
        )

    def retrieve_user_session(self, token: str) -> LoggedUser:
        user_id = self.__jwt_service.verify_access_token(token)

        user = self.__user_repository.get_user_by_id(user_id)
        if not user:
            self.__logger.warning(
                f"Token validation failed: User with id {user_id} does not exist"
            )
            raise InternalAuthError("Valid token for inexistent user")

        profile = self.__user_repository.get_user_profile_by_id(user_id)
        if not profile:
            self.__logger.warning(
                f"Token validation failed: User profile with id {user_id} does not exist"
            )
            raise InternalAuthError("Valid token for user without profile")

        return LoggedUser(
            id=user.id,
            email=user.email,
            name=profile.name,
            rating=profile.rating,
        )
