import os
import subprocess
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import make_url
from sqlmodel import Session, create_engine
from testcontainers.postgres import PostgresContainer

from marketplace_andes.app import app
from marketplace_andes.db.config import EngineConfig
from marketplace_andes.db.dependencies import get_db_config
from marketplace_andes.auth.user.repository import AuthUserRepository
from marketplace_andes.users.repository import UserRepository
from marketplace_andes.auth.password.dependencies import get_password_hasher


@pytest.fixture(scope="session")
def postgres_container():
    container = PostgresContainer(
        "postgres:18.3-trixie",
        username="backend_user",
        password="password",
        dbname="marketplace",
        driver="psycopg",
    )
    with container:
        yield container


@pytest.fixture(scope="session")
def migrated_postgres_container(
    postgres_container,
):
    test_db_url = postgres_container.get_connection_url()
    parsed_db_url = make_url(test_db_url)
    migrations_dir = Path(__file__).resolve().parents[2] / "migrations"
    env = os.environ.copy()
    env.pop("VIRTUAL_ENV", None)  # in case of running of an venv
    env.update({
        "PG_BACKEND_MIGRATION_USER": parsed_db_url.username or "",
        "PG_BACKEND_MIGRATION_PASSWORD": parsed_db_url.password or "",
        "PG_BACKEND_MIGRATION_HOST": parsed_db_url.host or "",
        "PG_BACKEND_MIGRATION_PORT": str(parsed_db_url.port or ""),
    })

    subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        cwd=migrations_dir,
        env=env,
        check=True,
    )

    yield postgres_container


@pytest.fixture(scope="session")
def get_db_test_engine(migrated_postgres_container):
    engine = create_engine(migrated_postgres_container.get_connection_url(), echo=True)
    yield engine


@pytest.fixture
def get_db_test_session(get_db_test_engine):
    with Session(get_db_test_engine) as session:
        yield session


@pytest.fixture
def get_test_client(migrated_postgres_container, get_db_test_engine):
    test_db_url = migrated_postgres_container.get_connection_url()

    def test_db_config():
        return EngineConfig(db_url=test_db_url, echo=True)

    app.dependency_overrides[get_db_config] = test_db_config

    with TestClient(app, client=("127.0.0.1", 50000)) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def get_test_password_hasher():
    return get_password_hasher()


@pytest.fixture
def get_setup_user(get_db_test_session: Session, get_test_password_hasher):
    def setup_user(username: str, password: str):
        user_repository = UserRepository(get_db_test_session)
        auth_user_repository = AuthUserRepository(get_db_test_session)

        user = user_repository.create_user(username)
        get_db_test_session.flush()
        auth_user = auth_user_repository.create_auth_user(
            user.id, get_test_password_hasher.hash(password)
        )
        get_db_test_session.commit()

        return user, auth_user

    return setup_user


@pytest.fixture
def get_tear_down_user(get_db_test_session: Session):
    def tear_down_user(user_id: UUID):
        user_repository = UserRepository(get_db_test_session)
        auth_user_repository = AuthUserRepository(get_db_test_session)

        user_repository.delete_user(user_id)
        get_db_test_session.flush()
        auth_user_repository.delete_auth_user(user_id)
        get_db_test_session.commit()

    return tear_down_user


@pytest.fixture
def get_test_user(get_setup_user, get_tear_down_user):
    username = "test_user"
    password = "secret-pass"
    user, auth_user = get_setup_user(username, password)
    yield user, auth_user, password
    get_tear_down_user(user.id)
