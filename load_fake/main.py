import os
import random
from uuid import UUID, uuid7
from datetime import datetime, UTC, timedelta

from sqlalchemy import Connection, create_engine, text

from argon2 import PasswordHasher


from fake import FAKE_NAMES, FAKE_SURNAMES

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

USER_DEV_PROFILES = [
    {
        "name": "Diego",
        "surname": "Rodríguez",
        "status": "student",
        "university": "Universidad de los Andes",
    },
    {
        "name": "Louise",
        "surname": "Fussien",
        "status": "student",
        "university": "Universidad de los Andes",
    },
    {
        "name": "Isaac",
        "surname": "Bermúdez",
        "status": "student",
        "university": "Universidad de los Andes",
    },
    {
        "name": "María Camila",
        "surname": "Martínez",
        "status": "student",
        "university": "Universidad de los Andes",
    },
    {
        "name": "Santiago",
        "surname": "Tenjov",
        "status": "student",
        "university": "Universidad de los Andes",
    },
    {
        "name": "Yesid",
        "surname": "Pineros",
        "status": "student",
        "university": "Universidad de los Andes",
    },
]


STATUSES = ["student", "professor", "admin", "assistant"]

UNIVERSITIES = [
    "Universidad de los Andes",
    "Universidad Nacional",
    "Pontificia Universidad Javeriana",
    "Universidad del Valle",
    "Universidad de Antioquia",
    "Universidad Industrial de Santander",
    "Universidad del Norte",
    "Universidad del Cauca",
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


def create_user_profile(
    conn: Connection,
    user_id: UUID,
    name: str,
    surname: str,
    status: str,
    university: str,
):
    """Create a user profile for the given user_id"""
    conn.execute(
        text(
            """
            INSERT INTO user_profiles (id, name, surname, status, university)
            VALUES (:id, :name, :surname, :status, :university)
            """
        ),
        {
            "id": user_id,
            "name": name,
            "surname": surname,
            "status": status,
            "university": university,
        },
    )


def create_fake_uwu_user_profile(conn: Connection, user_id: UUID):
    """Create profile for the uwu user"""
    create_user_profile(
        conn, user_id, None, None, "student", "The Academy of Advanced Procrastination"
    )


def create_fake_dev_user_profiles(conn: Connection, user_ids: list[UUID]):
    """Create profiles for dev users"""
    for user_id, profile in zip(user_ids, USER_DEV_PROFILES):
        create_user_profile(
            conn,
            user_id,
            profile["name"],
            profile["surname"],
            profile["status"],
            profile["university"],
        )


def create_fake_user_profiles(conn: Connection, user_ids: list[UUID]):
    """Create profiles for fake users"""
    for user_id in user_ids:
        name = random.choice(FAKE_NAMES)
        surname = random.choice(FAKE_SURNAMES)
        status = random.choice(STATUSES)
        university = random.choice(UNIVERSITIES)

        create_user_profile(conn, user_id, name, surname, status, university)


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
                "hashed_password": PASSWORD_HASHER.hash("password"),
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


def create_fake_users_spread(conn: Connection) -> tuple[list[UUID], list[UUID]]:
    """Create 2000+ users with creation dates from yesterday to 2 years ago, some with deleted_at"""
    user_ids: list[UUID] = []
    active_user_ids: list[UUID] = []
    users_data = []
    auth_users_data = []

    now = datetime.now(UTC)

    for i in range(2000):
        # Random creation date between 2 years ago and yesterday
        days_ago = random.randint(1, 730)
        created_at = now - timedelta(days=days_ago)

        # 15% chance of being deleted
        is_deleted = random.random() < 0.15

        # If deleted, calculate deleted_at between created_at and yesterday
        deleted_at = None
        if is_deleted:
            max_days_for_deletion = days_ago - 1  # Can't delete before creation
            if max_days_for_deletion > 0:
                deletion_days_ago = random.randint(1, max_days_for_deletion)
                deleted_at = now - timedelta(days=deletion_days_ago)

        user_id = uuid7()
        username = f"spread_user_{i + 1:04d}"

        users_data.append(
            {
                "id": user_id,
                "username": username,
                "created_at": created_at,
                "updated_at": deleted_at if deleted_at else created_at,
                "deleted_at": deleted_at,
            }
        )

        auth_users_data.append(
            {
                "id": user_id,
                "hashed_password": PASSWORD_HASHER.hash(f"{username}_pwd"),
            }
        )

        user_ids.append(user_id)
        if deleted_at is None:
            active_user_ids.append(user_id)

    conn.execute(
        text(
            """
            INSERT INTO users (id, username, created_at, updated_at, deleted_at)
            VALUES (:id, :username, :created_at, :updated_at, :deleted_at)
            """
        ),
        users_data,
    )

    conn.execute(
        text(
            """
            INSERT INTO auth_users (id, hashed_password)
            VALUES (:id, :hashed_password)
            """
        ),
        auth_users_data,
    )

    return user_ids, active_user_ids


def _create_follow_rows(
    user_ids: list[UUID],
    follow_pairs_state: set[tuple[UUID, UUID]],
    created_at_factory,
) -> list[dict]:
    follows_data = []

    for follower_id in user_ids:
        possible_followed_ids = [
            user_id for user_id in user_ids if user_id != follower_id
        ]
        if not possible_followed_ids:
            continue

        follow_count = random.randint(0, min(10, len(possible_followed_ids)))
        if follow_count == 0:
            continue

        for followed_id in random.sample(possible_followed_ids, follow_count):
            pair = (follower_id, followed_id)
            if pair in follow_pairs_state:
                continue

            follows_data.append(
                {
                    "follower_id": follower_id,
                    "followed_id": followed_id,
                    "created_at": created_at_factory(),
                }
            )
            follow_pairs_state.add(pair)

    return follows_data


def create_fake_follows_now(
    conn: Connection,
    user_ids: list[UUID],
    follow_pairs_state: set[tuple[UUID, UUID]],
):
    follows_data = _create_follow_rows(
        user_ids,
        follow_pairs_state,
        created_at_factory=lambda: datetime.now(UTC),
    )

    if follows_data:
        conn.execute(
            text(
                """
                INSERT INTO user_follows (follower_id, followed_id, created_at)
                VALUES (:follower_id, :followed_id, :created_at)
                """
            ),
            follows_data,
        )


def create_fake_follows_now_spread(
    conn: Connection,
    user_ids: list[UUID],
    follow_pairs_state: set[tuple[UUID, UUID]],
):
    now = datetime.now(UTC)
    follows_data = _create_follow_rows(
        user_ids,
        follow_pairs_state,
        created_at_factory=lambda: now - timedelta(days=random.randint(1, 730)),
    )

    if follows_data:
        conn.execute(
            text(
                """
                INSERT INTO user_follows (follower_id, followed_id, created_at)
                VALUES (:follower_id, :followed_id, :created_at)
                """
            ),
            follows_data,
        )


def create_fake_dev_follows(
    conn: Connection,
    dev_user_ids: list[UUID],
    follow_pairs_state: set[tuple[UUID, UUID]],
):
    """Make every dev user follow every other dev user."""
    follows_data = []

    for follower_id in dev_user_ids:
        for followed_id in dev_user_ids:
            if follower_id == followed_id:
                continue

            pair = (follower_id, followed_id)
            if pair in follow_pairs_state:
                continue

            follows_data.append(
                {
                    "follower_id": follower_id,
                    "followed_id": followed_id,
                    "created_at": datetime.now(UTC),
                }
            )
            follow_pairs_state.add(pair)

    if follows_data:
        conn.execute(
            text(
                """
                INSERT INTO user_follows (follower_id, followed_id, created_at)
                VALUES (:follower_id, :followed_id, :created_at)
                """
            ),
            follows_data,
        )


def main():
    engine = create_engine(
        f"postgresql+psycopg://postgres:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/marketplace",  # do it as root
        echo=DB_ECHO,
    )
    with engine.begin() as conn:
        active_user_ids: list[UUID] = []
        follow_pairs_state: set[tuple[UUID, UUID]] = set()

        uwu_user_id = create_fake_uwu_user(conn)
        active_user_ids.append(uwu_user_id)
        create_fake_uwu_user_profile(conn, uwu_user_id)

        dev_user_ids = create_fake_dev_users(conn)
        active_user_ids.extend(dev_user_ids)
        create_fake_dev_user_profiles(conn, dev_user_ids)

        user_ids = create_fake_users(conn)
        active_user_ids.extend(user_ids)
        create_fake_user_profiles(conn, user_ids)

        spread_user_ids, spread_active_user_ids = create_fake_users_spread(conn)
        active_user_ids.extend(spread_active_user_ids)
        create_fake_user_profiles(conn, spread_user_ids)

        create_fake_dev_follows(conn, dev_user_ids, follow_pairs_state)
        create_fake_follows_now(conn, active_user_ids, follow_pairs_state)
        create_fake_follows_now_spread(conn, spread_active_user_ids, follow_pairs_state)


if __name__ == "__main__":
    main()
