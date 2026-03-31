from datetime import datetime, UTC
from uuid import UUID, uuid7

from sqlmodel import Session, select, update, col

from .models import AuthSession


class AuthSessionRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_session(
        self, user_id: UUID, token_hash: str, expires_at: datetime, anon_ip: str
    ) -> AuthSession:
        auth_session = AuthSession(
            id=uuid7(),
            user_id=user_id,
            refresh_token_hash=token_hash,
            ip_address=anon_ip,
            expires_at=expires_at,
            created_at=datetime.now(UTC),
        )
        self.session.add(auth_session)
        return auth_session

    def revoke_session(self, session_id: UUID) -> None:
        stmt = (
            update(AuthSession)
            .where(col(AuthSession.id) == session_id)
            .values(revoked_at=datetime.now(UTC))
        )
        self.session.exec(stmt)

    def get_session_status_by_id(
        self, session_id: UUID
    ) -> tuple[str, datetime, datetime | None] | None:
        stmt = select(
            AuthSession.refresh_token_hash,
            AuthSession.expires_at,
            AuthSession.revoked_at,
        ).where(AuthSession.id == session_id)
        return self.session.exec(stmt).first()

    def get_session_by_refresh_token_hash(self, token_hash: str) -> AuthSession | None:
        stmt = select(AuthSession).where(AuthSession.refresh_token_hash == token_hash)
        return self.session.exec(stmt).first()
