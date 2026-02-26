import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, delete

from backend.auth.models import User
from backend.config import get_settings
from backend.database import get_engine


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return "postgresql+psycopg://postgres:postgres@db:5432/marketplace"


@pytest.fixture(scope="session", autouse=True)
def configure_test_environment(test_database_url: str) -> None:
    os.environ["DATABASE_URL"] = test_database_url
    os.environ["JWT_SECRET_KEY"] = "test-secret-key"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "60"
    get_settings.cache_clear()
    get_engine.cache_clear()
    yield
    get_engine.cache_clear()
    get_settings.cache_clear()


@pytest.fixture
def db_session(configure_test_environment: None) -> Session:
    _ = configure_test_environment
    engine = get_engine()
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        session.exec(delete(User))
        session.commit()
        yield session
        session.exec(delete(User))
        session.commit()


@pytest.fixture
def client(db_session: Session) -> TestClient:
    _ = db_session
    from backend.app import app

    with TestClient(app) as test_client:
        yield test_client
