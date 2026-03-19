from sqlmodel import Session, create_engine, text


def test_db_connection(setup_postgres):
    engine = create_engine(setup_postgres)

    with Session(engine) as session:
        connection = session.connection()

        current_user = connection.execute(text("SELECT current_user")).scalar_one()
        assert current_user == "backend_user"

        pg_version = connection.execute(text("SELECT version()")).scalar_one()
        assert "PostgreSQL" in pg_version
        assert "18.3" in pg_version
