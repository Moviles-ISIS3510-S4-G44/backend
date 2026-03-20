import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.marketplace_andes_backend.app import app
from src.marketplace_andes_backend.config import get_settings
from src.marketplace_andes_backend.db import get_engine, get_session
from testcontainers.postgres import PostgresContainer


TOP_LEVEL_DIR = Path(__file__).resolve().parent

os.environ["ENV_FILE"] = str(TOP_LEVEL_DIR / ".env.test")
os.environ.setdefault("TESTCONTAINERS_RYUK_DISABLED", "true")


PG_CONTAINER = PostgresContainer(
    "postgres:18.3-trixie",
    username="backend_user",
    password="password",
    dbname="marketplace",
    driver="psycopg",
)


@pytest.fixture(scope="session", autouse=True)
def setup_postgres(request):
    PG_CONTAINER.start()

    conn_url = PG_CONTAINER.get_connection_url()
    parsed_url = urlsplit(conn_url)

    os.environ["db_host"] = parsed_url.hostname or "localhost"
    os.environ["db_port"] = str(parsed_url.port or 5432)
    os.environ["db_password"] = parsed_url.password or "password"

    # Tests use the container default user for both app queries and migrations.
    os.environ["PG_BACKEND_MIGRATION_USER"] = parsed_url.username or "backend_user"
    os.environ["PG_BACKEND_MIGRATION_HOST"] = parsed_url.hostname or "localhost"
    os.environ["PG_BACKEND_MIGRATION_PORT"] = str(parsed_url.port or 5432)
    os.environ["PG_BACKEND_MIGRATION_PASSWORD"] = parsed_url.password or "password"

    get_settings.cache_clear()
    get_engine.cache_clear()

    alembic_config = Config()
    alembic_config.set_main_option(
        "script_location", str(TOP_LEVEL_DIR.parent / "alembic")
    )
    alembic_config.set_main_option("path_separator", "os")
    alembic_config.set_main_option("prepend_sys_path", ".")
    command.upgrade(alembic_config, "head")

    def remove_container():
        PG_CONTAINER.stop()

    request.addfinalizer(remove_container)

    return conn_url


@pytest.fixture
def session():
    engine = get_engine()
    connection = engine.connect()
    transaction = connection.begin()

    session = Session(bind=connection)
    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(session: Session):
    def get_test_session():
        yield session

    app.dependency_overrides[get_session] = get_test_session

    client = TestClient(app)
    yield client

    app.dependency_overrides.clear()
