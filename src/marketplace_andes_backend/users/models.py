from uuid import UUID, uuid7

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: UUID = Field(default_factory=uuid7, primary_key=True)
    university_id: UUID | None = Field(default=None, foreign_key="university.id", index=True)
    program_id: UUID | None = Field(default=None, foreign_key="program.id", index=True)
    name: str
    email: str = Field(index=True, unique=True)
    rating: int = Field(default=0, ge=0, le=5)
    is_verified: bool = Field(default=False)
    student_code: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    last_login_at: datetime | None = None
