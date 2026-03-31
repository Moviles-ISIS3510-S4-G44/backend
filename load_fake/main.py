import os
import random
from uuid import UUID, uuid7
from datetime import datetime, UTC

from sqlalchemy import Connection, create_engine, text

from argon2 import PasswordHasher


DB_HOST = os.getenv("PG_HOST", "postgres")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_PASSWORD = os.getenv("PG_PASSWORD", "password")
DB_ECHO = os.getenv("PG_ECHO", "1") == "1"
RANDOM_SEED = os.getenv("RANDOM_SEED", "42")

random.seed(int(RANDOM_SEED))

N_USERS = 10

PASSWORD_HASHER = PasswordHasher()

USERS_DEV = [
    "da.rodriguezv1",
    "l.fussien",
    "i.bermudezl",
    "mc.martinezm1",
    "s.tenjov",
    "y.pineros",
]


def create_fake_uwu_user(conn: Connection):
    """This user always is created"""
    username = "uwu"
    password = "password"

    result = conn.execute(
        text(
            """
            INSERT INTO users (id, username, created_at, updated_at)
            VALUES (:id, :username, :created_at, :updated_at)
            RETURNING id
            
            """
        ),
        {
            "id": uuid7(),
            "username": username,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        },
    )
    user_id = result.scalar_one()

    conn.execute(
        text(
            """
            INSERT INTO auth_users (id, hashed_password)
            VALUES (:id, :hashed_password)
            """
        ),
        {
            "id": user_id,
            "hashed_password": PASSWORD_HASHER.hash(password),
        },
    )

    return user_id


def create_fake_dev_users(conn: Connection) -> list[UUID]:
    user_ids: list[UUID] = []
    for username in USERS_DEV:
        user_result = conn.execute(
            text(
                """
                INSERT INTO users (id, username, created_at, updated_at)
                VALUES (:id, :username, :created_at, :updated_at)
                RETURNING id
                """
            ),
            {
                "id": uuid7(),
                "username": username,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
        )
        user_id = user_result.scalar_one()

        conn.execute(
            text(
                """
                INSERT INTO auth_users (id, hashed_password)
                VALUES (:id, :hashed_password)
                """
            ),
            {
                "id": user_id,
                "hashed_password": PASSWORD_HASHER.hash(f"{username}_pwd"),
            },
        )
        user_ids.append(user_id)

    return user_ids


def create_fake_users(conn: Connection) -> list[UUID]:
    user_ids: list[UUID] = []
    for index in range(N_USERS):
        username = f"user_{index + 1:02d}"
        user_result = conn.execute(
            text(
                """
                INSERT INTO users (id, username, created_at, updated_at)
                VALUES (:id, :username, :created_at, :updated_at)
                RETURNING id
                """
            ),
            {
                "id": uuid7(),
                "username": username,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            },
        )
        user_id = user_result.scalar_one()

        conn.execute(
            text(
                """
                INSERT INTO auth_users (id, hashed_password)
                VALUES (:id, :hashed_password)
                """
            ),
            {
                "id": user_id,
                "hashed_password": PASSWORD_HASHER.hash(f"{username}_pwd"),
            },
        )
        user_ids.append(user_id)

    return user_ids


def main():
    engine = create_engine(
        f"postgresql+psycopg://postgres:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/marketplace",  # do it as root
        echo=DB_ECHO,
    )
    with engine.begin() as conn:
        uwu_user_id = create_fake_uwu_user(conn)
        dev_user_ids = create_fake_dev_users(conn)
        user_ids = create_fake_users(conn)


if __name__ == "__main__":
    main()
