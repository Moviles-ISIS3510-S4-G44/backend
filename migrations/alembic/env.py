import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


def get_db_url():
    pg_user = os.getenv("PG_BACKEND_MIGRATION_USER", "backend_migration_user")
    pg_password = os.getenv("PG_BACKEND_MIGRATION_PASSWORD", "password")
    pg_host = os.getenv("PG_BACKEND_MIGRATION_HOST", "db")
    pg_port = os.getenv("PG_BACKEND_MIGRATION_PORT", "5432")
    pg_db = os.getenv("PG_BACKEND_MIGRATION_DB", "marketplace")

    return (
        f"postgresql+psycopg://{pg_user}:{pg_password}"
        f"@{pg_host}:{pg_port}/{pg_db}"
    )


config = context.config
config.set_main_option("sqlalchemy.url", get_db_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()