from datetime import UTC, datetime
from uuid import UUID, uuid7

from sqlmodel import Session, select, delete, col

from .models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_id_from_username(self, username: str) -> UUID | None:
        stmt = select(User.id).where(User.username == username)
        result = self.session.exec(stmt).first()
        return result

    def get_username_from_id(self, user_id: UUID) -> str | None:
        stmt = select(User.username).where(User.id == user_id)
        result = self.session.exec(stmt).first()
        return result

    def create_user(self, username: str) -> User:
        now = datetime.now(UTC)
        user = User(id=uuid7(), username=username, created_at=now, updated_at=now)
        self.session.add(user)
        return user

    def delete_user(self, user_id: UUID) -> bool:
        stmt = delete(User).where(col(User.id) == user_id)
        result = self.session.exec(stmt)
        return result.rowcount == 1

    def delete_all_users(self) -> int:
        stmt = delete(User)
        result = self.session.exec(stmt)
        return result.rowcount or 0
