import os
import random
from enum import StrEnum
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
N_LISTINGS = 500

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
        "rating": 5,
    },
    {
        "name": "Louise",
        "surname": "Fussien",
        "status": "student",
        "university": "Universidad de los Andes",
        "rating": 4,
    },
    {
        "name": "Isaac",
        "surname": "Bermúdez",
        "status": "student",
        "university": "Universidad de los Andes",
        "rating": 5,
    },
    {
        "name": "María Camila",
        "surname": "Martínez",
        "status": "student",
        "university": "Universidad de los Andes",
        "rating": 4,
    },
    {
        "name": "Santiago",
        "surname": "Tenjov",
        "status": "student",
        "university": "Universidad de los Andes",
        "rating": 3,
    },
    {
        "name": "Yesid",
        "surname": "Pineros",
        "status": "student",
        "university": "Universidad de los Andes",
        "rating": 5,
    },
]

# Realistic rating weights: most marketplace ratings skew high
RATING_WEIGHTS = [2, 5, 10, 25, 58]  # 1★ through 5★


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
    name: str | None,
    surname: str | None,
    status: str,
    university: str,
    rating: int | None = None,
):
    """Create a user profile for the given user_id.

    name and surname can be None for placeholder/system users.
    """
    conn.execute(
        text(
            """
            INSERT INTO user_profiles (id, name, surname, status, university, rating)
            VALUES (:id, :name, :surname, :status, :university, :rating)
            """
        ),
        {
            "id": user_id,
            "name": name,
            "surname": surname,
            "status": status,
            "university": university,
            "rating": rating,
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
            profile["rating"],
        )


def create_fake_user_profiles(conn: Connection, user_ids: list[UUID]):
    """Create profiles for fake users"""
    for user_id in user_ids:
        name = random.choice(FAKE_NAMES)
        surname = random.choice(FAKE_SURNAMES)
        status = random.choice(STATUSES)
        university = random.choice(UNIVERSITIES)
        rating = random.choices([1, 2, 3, 4, 5], weights=RATING_WEIGHTS)[0]

        create_user_profile(conn, user_id, name, surname, status, university, rating)


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


def create_fake_users_spread(conn: Connection) -> list[UUID]:
    """Create 2000+ users with creation dates from yesterday to 2 years ago, some with deleted_at"""
    user_ids: list[UUID] = []
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

    return user_ids


LISTING_TITLES = [
    "iPhone 14 Pro 256GB",
    "MacBook Air M2",
    "Cien años de soledad",
    "Escritorio en madera de roble",
    'Monitor LG UltraWide 29"',
    "Silla ergonómica para oficina",
    "Clean Code en español",
    "Teclado mecánico Keychron K2",
    "AirPods Pro 2da gen",
    "Kindle Paperwhite",
    "Mochila Samsonite para laptop",
    "Cálculo de Larson 12a edición",
    "Arduino Starter Kit",
    "Raspberry Pi 4 Model B",
    "Audífonos Sony WH-1000XM5",
    "Cámara Canon EOS M50",
    "Álgebra lineal de Grossman",
    "Mesa auxiliar plegable",
    "Lámpara de escritorio LED",
    "Cable USB-C a HDMI 4K",
]


class ListingCondition(StrEnum):
    NEW = "new"
    USED = "used"
    REFURBISHED = "refurbished"


LISTING_CONDITIONS = list(ListingCondition)
LISTING_LOCATIONS = [
    "Bogotá",
    "Medellín",
    "Cali",
    "Barranquilla",
    "Bucaramanga",
]
DEFAULT_CATEGORIES = [
    "Electronics",
    "Books",
    "Furniture",
    "Accessories",
    "Home",
]

PUBLISHED_RATIO = 0.80
SOLD_AFTER_PUBLISH_RATIO = 0.35


def ensure_categories(conn: Connection) -> list[UUID]:
    existing_category_ids = [
        row[0] for row in conn.execute(text("SELECT id FROM categories")).all()
    ]
    if existing_category_ids:
        return existing_category_ids

    categories_data = [
        {
            "id": uuid7(),
            "name": name,
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        for name in DEFAULT_CATEGORIES
    ]
    conn.execute(
        text(
            """
            INSERT INTO categories (id, name, created_at, updated_at)
            VALUES (:id, :name, :created_at, :updated_at)
            """
        ),
        categories_data,
    )
    return [item["id"] for item in categories_data]


def create_fake_listings(
    conn: Connection,
    seller_ids: list[UUID],
    category_ids: list[UUID],
) -> None:
    """Seed listings and status history."""
    now = datetime.now(UTC)
    listings_data: list[dict] = []
    history_data: list[dict] = []

    for i in range(N_LISTINGS):
        listing_id = uuid7()
        seller_id = random.choice(seller_ids)
        category_id = random.choice(category_ids)

        # Random creation date between 1 year ago and 3 days ago
        days_ago = random.randint(3, 365)
        created_at = now - timedelta(days=days_ago)

        title = f"{random.choice(LISTING_TITLES)} #{i + 1:03d}"
        condition = random.choice(LISTING_CONDITIONS).value
        price = random.randint(10000, 5000000)
        location = random.choice(LISTING_LOCATIONS)
        images = [
            f"https://picsum.photos/seed/{listing_id.hex}-{img}/900/900"
            for img in range(1, random.randint(2, 5))
        ]

        # 80% of listings reach published, 20% stay as draft
        reaches_published = random.random() < PUBLISHED_RATIO

        published_at = None
        sold_at = None
        if reaches_published:
            status = "published"
            # Time to publish: between 5 minutes and 72 hours
            publish_delay_minutes = random.randint(5, 4320)
            published_at = created_at + timedelta(minutes=publish_delay_minutes)

            # Some published listings are sold after publication.
            reaches_sold = random.random() < SOLD_AFTER_PUBLISH_RATIO
            if reaches_sold:
                # Sold between 1 hour and 120 days after publication.
                sold_delay_minutes = random.randint(60, 172800)
                sold_at = published_at + timedelta(minutes=sold_delay_minutes)
                if sold_at > now:
                    sold_at = now - timedelta(minutes=random.randint(1, 180))
                if sold_at <= published_at:
                    sold_at = published_at + timedelta(minutes=1)
                status = "sold"
                updated_at = sold_at
            else:
                updated_at = published_at
        else:
            status = "draft"
            updated_at = created_at

        listings_data.append(
            {
                "id": listing_id,
                "seller_id": seller_id,
                "category_id": category_id,
                "title": title,
                "description": f"Listing #{i + 1} — {condition} item.",
                "condition": condition,
                "price": price,
                "images": images,
                "status": status,
                "location": location,
                "created_at": created_at,
                "updated_at": updated_at,
            }
        )

        # Status history: always record the initial draft event
        history_data.append(
            {
                "id": uuid7(),
                "listing_id": listing_id,
                "from_status": None,
                "to_status": "draft",
                "changed_at": created_at,
            }
        )

        if reaches_published:
            history_data.append(
                {
                    "id": uuid7(),
                    "listing_id": listing_id,
                    "from_status": "draft",
                    "to_status": "published",
                    "changed_at": published_at,
                }
            )

        if sold_at is not None:
            history_data.append(
                {
                    "id": uuid7(),
                    "listing_id": listing_id,
                    "from_status": "published",
                    "to_status": "sold",
                    "changed_at": sold_at,
                }
            )

    conn.execute(
        text(
            """
            INSERT INTO listings (id, seller_id, category_id, title, description, condition, price, images, status, location, created_at, updated_at)
            VALUES (:id, :seller_id, :category_id, :title, :description, :condition, :price, :images, :status, :location, :created_at, :updated_at)
            """
        ),
        listings_data,
    )

    conn.execute(
        text(
            """
            INSERT INTO listing_status_history (id, listing_id, from_status, to_status, changed_at)
            VALUES (:id, :listing_id, :from_status, :to_status, :changed_at)
            """
        ),
        history_data,
    )

    print(
        f"Seeded {len(listings_data)} listings with {len(history_data)} status history entries."
    )


def main():
    engine = create_engine(
        f"postgresql+psycopg://postgres:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/marketplace",  # do it as root
        echo=DB_ECHO,
    )
    with engine.begin() as conn:
        existing_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
        existing_listings = conn.execute(
            text("SELECT COUNT(*) FROM listings")
        ).scalar_one()
        category_ids = ensure_categories(conn)

        if existing_users > 0 and existing_listings > 0:
            print(
                f"Database already has {existing_users} users and {existing_listings} listings — skipping seed. "
                "Run 'docker compose down -v' to reset."
            )
            return

        if existing_users > 0 and existing_listings == 0:
            # In this fake dataset every existing user can act as seller.
            seller_ids = [
                row[0] for row in conn.execute(text("SELECT id FROM users")).all()
            ]
            create_fake_listings(conn, seller_ids, category_ids)
            print(f"Database already had users; seeded {N_LISTINGS} listings.")
            return

        uwu_user_id = create_fake_uwu_user(conn)
        create_fake_uwu_user_profile(conn, uwu_user_id)

        dev_user_ids = create_fake_dev_users(conn)
        create_fake_dev_user_profiles(conn, dev_user_ids)

        user_ids = create_fake_users(conn)
        create_fake_user_profiles(conn, user_ids)

        spread_user_ids = create_fake_users_spread(conn)
        create_fake_user_profiles(conn, spread_user_ids)

        all_seller_ids = [uwu_user_id] + dev_user_ids + user_ids
        create_fake_listings(conn, all_seller_ids, category_ids)


if __name__ == "__main__":
    main()
