from uuid import UUID

from sqlmodel import Session, select, delete, col

from .models import AuthUser


class AuthUserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_auth_user_by_id(self, user_id: UUID) -> AuthUser | None:
        stmt = select(AuthUser).where(AuthUser.id == user_id)
        return self.session.exec(stmt).first()

    def auth_user_exists(self, user_id: UUID) -> bool:
        stmt = select(AuthUser).where(AuthUser.id == user_id)
        return self.session.exec(stmt).first() is not None

    def get_hashed_password(self, user_id: UUID) -> str | None:
        stmt = select(AuthUser.hashed_password).where(AuthUser.id == user_id)
        return self.session.exec(stmt).first()

    def create_auth_user(self, user_id: UUID, hashed_password: str) -> AuthUser:
        auth_user = AuthUser(id=user_id, hashed_password=hashed_password)
        self.session.add(auth_user)
        return auth_user

    def delete_auth_user(self, user_id: UUID) -> bool:
        stmt = delete(AuthUser).where(col(AuthUser.id) == user_id)
        result = self.session.exec(stmt)
        return result.rowcount == 1
