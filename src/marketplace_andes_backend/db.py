from collections.abc import Generator
from functools import lru_cache

from sqlalchemy.engine import Engine
from sqlmodel import Session, create_engine

from .config import get_settings


@lru_cache
def get_engine() -> Engine:
    settings = get_settings()
    return create_engine(settings.database_url, echo=settings.database_echo)


def get_session() -> Generator[Session, None, None]:
    with Session(get_engine()) as session:
        yield session
