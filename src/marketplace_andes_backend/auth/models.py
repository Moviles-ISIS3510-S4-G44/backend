from uuid import UUID

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class UserAuth(SQLModel, table=True):
    __tablename__ = "user_auth"
    __table_args__ = (CheckConstraint("id = user_id", name="ck_user_auth_id_matches_user_id"),)

    id: UUID = Field(primary_key=True, foreign_key="user.id")
    user_id: UUID = Field(foreign_key="user.id", index=True, unique=True)
    hashed_password: str
