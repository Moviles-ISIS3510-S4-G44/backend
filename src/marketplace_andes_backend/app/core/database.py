from sqlmodel import SQLModel, create_engine

from .config import get_settings

settings = get_settings()
engine = create_engine(settings.database_url, echo=settings.sql_echo)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

