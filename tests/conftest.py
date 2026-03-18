import os
from pathlib import Path

import pytest

from testcontainers.postgres import PostgresContainer


TOP_LEVEL_DIR = Path(__file__).resolve().parent

os.environ["ENV_FILE"] = str(TOP_LEVEL_DIR / ".env.test")


PG_CONTAINER = PostgresContainer(
    "postgres:18.3-trixie",
    username="backend_user",
    password="password",
    dbname="marketplace",
    driver="psycopg",
)


@pytest.fixture(scope="session", autouse=True)
def setup(request):
    PG_CONTAINER.start()

    conn_url = PG_CONTAINER.get_connection_url()
    os.environ["DATABASE_URL"] = conn_url

    def remove_container():
        PG_CONTAINER.stop()

    request.addfinalizer(remove_container)
