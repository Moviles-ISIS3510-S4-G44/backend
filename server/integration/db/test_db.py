from sqlmodel import text


def test_db_connection(get_db_test_session):
    connection = get_db_test_session.connection()

    current_user = connection.execute(text("SELECT current_user")).scalar_one()
    assert current_user == "backend_user"

    pg_version = connection.execute(text("SELECT version()")).scalar_one()
    assert "PostgreSQL" in pg_version
    assert "18.3" in pg_version
