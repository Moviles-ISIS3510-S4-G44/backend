from sqlmodel import Session, select

from .models import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_user(self, user: User) -> User:
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def list_users(self) -> list[User]:
        statement = select(User).order_by(User.name.asc())
        return list(self.session.exec(statement))
