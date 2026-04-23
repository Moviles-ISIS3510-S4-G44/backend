import os
import random
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid7

from argon2 import PasswordHasher
from sqlalchemy import Connection, create_engine, text

from fake import FAKE_NAMES, FAKE_SURNAMES

DB_HOST = os.getenv("PG_HOST", "postgres")
DB_PORT = os.getenv("PG_PORT", "5432")
DB_PASSWORD = os.getenv("PG_PASSWORD", "password")
DB_ECHO = os.getenv("PG_ECHO", "1") == "1"
RANDOM_SEED = os.getenv("RANDOM_SEED", "42")

random.seed(int(RANDOM_SEED))

N_USERS = 30
N_HISTORICAL_USERS = 300
N_LISTINGS = 500
N_INTERACTIONS = 2000

PASSWORD_HASHER = PasswordHasher()

DEV_USERS: list[dict[str, str | int]] = [
    {
        "email": "da.rodriguezv1@uniandes.edu.co",
        "name": "Diego Rodríguez",
        "rating": 5,
    },
    {
        "email": "l.fussien@uniandes.edu.co",
        "name": "Louise Fussien",
        "rating": 4,
    },
    {
        "email": "i.bermudezl@uniandes.edu.co",
        "name": "Isaac Bermúdez",
        "rating": 5,
    },
    {
        "email": "mc.martinezm1@uniandes.edu.co",
        "name": "María Camila Martínez",
        "rating": 4,
    },
    {
        "email": "s.tenjov@uniandes.edu.co",
        "name": "Santiago Tenjov",
        "rating": 3,
    },
    {
        "email": "y.pineros@uniandes.edu.co",
        "name": "Yesid Pineros",
        "rating": 5,
    },
]

# Realistic rating weights: most marketplace ratings skew high
RATING_WEIGHTS = [2, 5, 10, 25, 58]  # 1★ through 5★

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


def create_user_with_profile(
    conn: Connection,
    *,
    email: str,
    password: str,
    name: str,
    rating: int,
    created_at: datetime | None = None,
    updated_at: datetime | None = None,
    deleted_at: datetime | None = None,
) -> UUID:
    now = datetime.now(UTC)
    created_at = created_at or now
    updated_at = updated_at or created_at

    user_result = conn.execute(
        text(
            """
            INSERT INTO users (id, email, created_at, updated_at, deleted_at)
            VALUES (:id, :email, :created_at, :updated_at, :deleted_at)
            RETURNING id
            """
        ),
        {
            "id": uuid7(),
            "email": email,
            "created_at": created_at,
            "updated_at": updated_at,
            "deleted_at": deleted_at,
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
            "hashed_password": PASSWORD_HASHER.hash(password),
        },
    )

    conn.execute(
        text(
            """
            INSERT INTO user_profiles (id, name, rating)
            VALUES (:id, :name, :rating)
            """
        ),
        {
            "id": user_id,
            "name": name,
            "rating": rating,
        },
    )

    return user_id


def create_fake_users(conn: Connection) -> list[UUID]:
    user_ids: list[UUID] = []

    for index in range(N_USERS):
        first_name = random.choice(FAKE_NAMES)
        surname = random.choice(FAKE_SURNAMES)
        full_name = f"{first_name} {surname}"
        local = f"user_{index + 1:03d}"
        email = f"{local}@marketplace.local"
        rating = random.choices([1, 2, 3, 4, 5], weights=RATING_WEIGHTS)[0]

        user_ids.append(
            create_user_with_profile(
                conn,
                email=email,
                password=f"{local}_pwd",
                name=full_name,
                rating=rating,
            )
        )

    return user_ids


def create_fake_dev_users(conn: Connection) -> list[UUID]:
    user_ids: list[UUID] = []

    for profile in DEV_USERS:
        email = str(profile["email"])
        name = str(profile["name"])
        rating = int(profile["rating"])
        local = email.split("@")[0]
        user_ids.append(
            create_user_with_profile(
                conn,
                email=email,
                password=f"{local}_pwd",
                name=name,
                rating=rating,
            )
        )

    return user_ids


def create_fake_uwu_user(conn: Connection) -> UUID:
    return create_user_with_profile(
        conn,
        email="uwu@marketplace.local",
        password="password",
        name="Uwu User",
        rating=5,
    )


def create_fake_users_spread(conn: Connection) -> list[UUID]:
    """Create users with creation dates between yesterday and 2 years ago."""
    user_ids: list[UUID] = []

    now = datetime.now(UTC)

    for i in range(N_HISTORICAL_USERS):
        days_ago = random.randint(1, 730)
        created_at = now - timedelta(days=days_ago)

        is_deleted = random.random() < 0.15 and days_ago > 1
        deleted_at = None
        if is_deleted:
            deletion_days_ago = random.randint(1, days_ago - 1)
            deleted_at = now - timedelta(days=deletion_days_ago)

        local = f"spread_user_{i + 1:04d}"
        first_name = random.choice(FAKE_NAMES)
        surname = random.choice(FAKE_SURNAMES)
        full_name = f"{first_name} {surname}"

        user_ids.append(
            create_user_with_profile(
                conn,
                email=f"{local}@marketplace.local",
                password=f"{local}_pwd",
                name=full_name,
                rating=random.choices([1, 2, 3, 4, 5], weights=RATING_WEIGHTS)[0],
                created_at=created_at,
                updated_at=deleted_at or created_at,
                deleted_at=deleted_at,
            )
        )

    return user_ids


def ensure_categories(conn: Connection) -> list[UUID]:
    existing_category_ids = [
        row[0] for row in conn.execute(text("SELECT id FROM categories")).all()
    ]
    if existing_category_ids:
        return existing_category_ids

    category_ids: list[UUID] = []
    categories_data: list[dict] = []
    for name in DEFAULT_CATEGORIES:
        category_id = uuid7()
        category_ids.append(category_id)
        categories_data.append(
            {
                "id": category_id,
                "name": name,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
        )
    conn.execute(
        text(
            """
            INSERT INTO categories (id, name, created_at, updated_at)
            VALUES (:id, :name, :created_at, :updated_at)
            """
        ),
        categories_data,
    )
    return category_ids


def create_fake_listings(
    conn: Connection,
    seller_ids: list[UUID],
    category_ids: list[UUID],
) -> list[UUID]:
    """Seed listings and status history."""
    now = datetime.now(UTC)
    listings_data: list[dict] = []
    history_data: list[dict] = []
    listing_ids: list[UUID] = []

    for i in range(N_LISTINGS):
        listing_id = uuid7()
        listing_ids.append(listing_id)

        seller_id = random.choice(seller_ids)
        category_id = random.choice(category_ids)

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

        reaches_published = random.random() < PUBLISHED_RATIO

        published_at = None
        sold_at = None
        if reaches_published:
            status = "published"
            publish_delay_minutes = random.randint(5, 4320)
            published_at = created_at + timedelta(minutes=publish_delay_minutes)

            reaches_sold = random.random() < SOLD_AFTER_PUBLISH_RATIO
            if reaches_sold:
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

    return listing_ids


def create_fake_purchases(conn: Connection, all_user_ids: list[UUID]) -> None:
    rows = conn.execute(
        text("""
            SELECT l.id, l.seller_id, l.price, lsh.changed_at AS sold_at
            FROM listings l
            JOIN listing_status_history lsh
              ON lsh.listing_id = l.id AND lsh.to_status = 'sold'
            WHERE l.status = 'sold'
        """)
    ).all()

    if not rows:
        return

    purchases_data: list[dict] = []
    for row in rows:
        eligible_buyers = [uid for uid in all_user_ids if uid != row.seller_id]
        buyer_id = random.choice(eligible_buyers)
        has_rating = random.random() < 0.70
        seller_rating = (
            random.choices([1, 2, 3, 4, 5], weights=RATING_WEIGHTS)[0] if has_rating else None
        )
        purchases_data.append(
            {
                "id": uuid7(),
                "listing_id": row.id,
                "buyer_id": buyer_id,
                "price_at_purchase": row.price,
                "purchased_at": row.sold_at,
                "seller_rating": seller_rating,
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO purchases (id, listing_id, buyer_id, price_at_purchase, purchased_at, seller_rating)
            VALUES (:id, :listing_id, :buyer_id, :price_at_purchase, :purchased_at, :seller_rating)
            ON CONFLICT (listing_id) DO NOTHING
            """
        ),
        purchases_data,
    )

    # Update each seller's profile rating to the rounded average of their received ratings
    conn.execute(
        text(
            """
            UPDATE user_profiles up
            SET rating = subq.avg_rating
            FROM (
                SELECT
                    l.seller_id,
                    ROUND(AVG(p.seller_rating)) AS avg_rating
                FROM purchases p
                JOIN listings l ON l.id = p.listing_id
                WHERE p.seller_rating IS NOT NULL
                GROUP BY l.seller_id
            ) subq
            WHERE up.id = subq.seller_id
            """
        )
    )

    print(f"Seeded {len(purchases_data)} purchases.")


def create_fake_interactions(
    conn: Connection,
    user_ids: list[UUID],
    listing_ids: list[UUID],
) -> None:
    now = datetime.now(UTC)

    listing_created_at: dict[UUID, datetime] = {
        row.id: row.created_at
        for row in conn.execute(
            text("SELECT id, created_at FROM listings WHERE id = ANY(:ids)"),
            {"ids": listing_ids},
        )
    }

    interactions_data: list[dict] = []

    for _ in range(N_INTERACTIONS):
        listing_id = random.choice(listing_ids)
        last_interaction_at = now - timedelta(
            days=random.randint(0, 180),
            minutes=random.randint(0, 1439),
        )
        created_at = listing_created_at.get(listing_id, last_interaction_at)
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)
        earliest = min(created_at, last_interaction_at)
        window_seconds = max(int((last_interaction_at - earliest).total_seconds()), 0)
        first_offset = random.randint(0, window_seconds) if window_seconds else 0
        first_interaction_at = earliest + timedelta(seconds=first_offset)

        interactions_data.append(
            {
                "id": uuid7(),
                "user_id": random.choice(user_ids),
                "listing_id": listing_id,
                "interaction_count": random.randint(1, 4),
                "first_interaction_at": first_interaction_at,
                "last_interaction_at": last_interaction_at,
            }
        )

    conn.execute(
        text(
            """
            INSERT INTO user_listing_interaction (
                id, user_id, listing_id, interaction_count,
                first_interaction_at, last_interaction_at
            )
            VALUES (
                :id, :user_id, :listing_id, :interaction_count,
                :first_interaction_at, :last_interaction_at
            )
            ON CONFLICT (user_id, listing_id)
            DO UPDATE SET
                interaction_count = user_listing_interaction.interaction_count + EXCLUDED.interaction_count,
                first_interaction_at = LEAST(
                    user_listing_interaction.first_interaction_at,
                    EXCLUDED.first_interaction_at
                ),
                last_interaction_at = GREATEST(
                    user_listing_interaction.last_interaction_at,
                    EXCLUDED.last_interaction_at
                )
            """
        ),
        interactions_data,
    )

    print(f"Processed {len(interactions_data)} interaction events.")


def main():
    engine = create_engine(
        f"postgresql+psycopg://postgres:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/marketplace",
        echo=DB_ECHO,
    )

    with engine.begin() as conn:
        existing_users = conn.execute(text("SELECT COUNT(*) FROM users")).scalar_one()
        existing_listings = conn.execute(
            text("SELECT COUNT(*) FROM listings")
        ).scalar_one()
        existing_interactions = conn.execute(
            text("SELECT COUNT(*) FROM user_listing_interaction")
        ).scalar_one()

        if existing_users == 0:
            create_fake_uwu_user(conn)
            dev_user_ids = create_fake_dev_users(conn)
            user_ids = create_fake_users(conn)
            spread_user_ids = create_fake_users_spread(conn)
            print(
                f"Seeded users/auth/profile: {1 + len(dev_user_ids) + len(user_ids) + len(spread_user_ids)}"
            )
        else:
            print(f"Database already has {existing_users} users.")

        category_ids = ensure_categories(conn)

        if existing_listings == 0:
            seller_ids = [
                row[0]
                for row in conn.execute(
                    text("SELECT id FROM users WHERE deleted_at IS NULL")
                ).all()
            ]
            listing_ids = create_fake_listings(conn, seller_ids, category_ids)
        else:
            listing_ids = [
                row[0] for row in conn.execute(text("SELECT id FROM listings")).all()
            ]
            print(f"Database already has {existing_listings} listings.")

        if existing_interactions == 0:
            user_ids_for_interactions = [
                row[0]
                for row in conn.execute(
                    text("SELECT id FROM users WHERE deleted_at IS NULL")
                ).all()
            ]
            create_fake_interactions(conn, user_ids_for_interactions, listing_ids)
        else:
            print(
                f"Database already has {existing_interactions} rows in user_listing_interaction."
            )

        existing_purchases = conn.execute(
            text("SELECT COUNT(*) FROM purchases")
        ).scalar_one()
        if existing_purchases == 0:
            all_user_ids = [
                row[0]
                for row in conn.execute(
                    text("SELECT id FROM users WHERE deleted_at IS NULL")
                ).all()
            ]
            create_fake_purchases(conn, all_user_ids)
        else:
            print(f"Database already has {existing_purchases} purchases.")


if __name__ == "__main__":
    main()
