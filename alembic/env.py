import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlmodel import SQLModel

from alembic import context

from src.marketplace_andes_backend.auth.models import UserAuth  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import Category  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import Listing  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import ListingMedia  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import ListingStatusHistory  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import MarketplaceTransaction  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import Message  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import MessageThread  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import Program  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import Review  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import SearchEvent  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import University  # noqa: F401
from src.marketplace_andes_backend.marketplace.models import UserActivityEvent  # noqa: F401
from src.marketplace_andes_backend.users.models import User  # noqa: F401


def get_db_url():
    PG_BACKEND_MIGRATION_USER = os.getenv(
        "PG_BACKEND_MIGRATION_USER", "backend_migration_user"
    )
    PG_BACKEND_MIGRATION_PASSWORD = os.getenv(
        "PG_BACKEND_MIGRATION_PASSWORD", "password"
    )
    PG_BACKEND_MIGRATION_HOST = os.getenv("PG_BACKEND_MIGRATION_HOST", "db")
    PG_BACKEND_MIGRATION_PORT = os.getenv("PG_BACKEND_MIGRATION_PORT", "5432")
    return f"postgresql+psycopg://{PG_BACKEND_MIGRATION_USER}:{PG_BACKEND_MIGRATION_PASSWORD}@{PG_BACKEND_MIGRATION_HOST}:{PG_BACKEND_MIGRATION_PORT}/marketplace"


config = context.config
config.set_main_option("sqlalchemy.url", get_db_url())

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata


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
