from uuid import UUID

from sqlmodel import Session, select

from ..models import User


class UserProfileService:
    def __init__(self, session: Session):
        self.session = session

    def get_info(self, user_id: UUID) -> User | None:
        statement = select(User).where(User.id == user_id)
        return self.session.exec(statement).first()
