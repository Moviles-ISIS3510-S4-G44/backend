from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlmodel import Field, SQLModel


class AuthUser(SQLModel, table=True):
    __tablename__ = "auth_users"

    id: UUID = Field(
        sa_column=sa.Column(
            postgresql.UUID(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        )
    )
    hashed_password: str = Field(sa_column=sa.Column(sa.Text(), nullable=False))
