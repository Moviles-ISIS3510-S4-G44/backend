from sqlmodel import Session, text

from src.marketplace_andes_backend.db import get_engine


def test_db_connection():
    with Session(get_engine()) as session:
        current_user = session.exec(text("SELECT current_user")).scalar_one()
        assert current_user == "backend_user"

        pg_version = session.exec(text("SELECT version()")).scalar_one()
        assert "PostgreSQL" in pg_version
        assert "18.3" in pg_version
