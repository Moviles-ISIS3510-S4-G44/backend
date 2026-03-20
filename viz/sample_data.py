from pathlib import Path
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import delete
from sqlmodel import Session

from src.marketplace_andes_backend.auth.models import UserAuth
from src.marketplace_andes_backend.auth.service import AuthService
from src.marketplace_andes_backend.db import get_engine
from src.marketplace_andes_backend.marketplace.models import (
    Category,
    Listing,
    ListingMedia,
    ListingStatusHistory,
    MarketplaceTransaction,
    Message,
    MessageThread,
    Program,
    Review,
    SearchEvent,
    University,
    UserActivityEvent,
)
from src.marketplace_andes_backend.users.models import User

BASE_TIME = datetime(2026, 1, 6, 9, tzinfo=UTC)


TABLE_MODELS = [
    Review,
    Message,
    MessageThread,
    SearchEvent,
    UserActivityEvent,
    MarketplaceTransaction,
    ListingMedia,
    ListingStatusHistory,
    Listing,
    Category,
    UserAuth,
    User,
    Program,
    University,
]


def reset_database(session: Session) -> None:
    for model in TABLE_MODELS:
        session.exec(delete(model))
    session.commit()


def _create_activity(
    user_id,
    event_type: str,
    created_at: datetime,
    listing_id=None,
    transaction_id=None,
) -> UserActivityEvent:
    return UserActivityEvent(
        user_id=user_id,
        listing_id=listing_id,
        transaction_id=transaction_id,
        event_type=event_type,
        created_at=created_at,
    )


def _seed_sample_data(session: Session) -> None:
    reset_database(session)

    auth_service = AuthService(session)
    seller_ratings = defaultdict(list)

    universities = [
        University(
            name="Uniandes",
            country="Colombia",
            city="Bogota",
            created_at=BASE_TIME - timedelta(days=90),
        ),
        University(
            name="Javeriana",
            country="Colombia",
            city="Bogota",
            created_at=BASE_TIME - timedelta(days=85),
        ),
        University(
            name="Universidad Nacional",
            country="Colombia",
            city="Bogota",
            created_at=BASE_TIME - timedelta(days=80),
        ),
    ]
    session.add_all(universities)
    session.flush()

    programs = [
        Program(
            university_id=universities[0].id,
            name="Systems Engineering",
            faculty="Engineering",
            created_at=BASE_TIME - timedelta(days=88),
        ),
        Program(
            university_id=universities[0].id,
            name="Industrial Engineering",
            faculty="Engineering",
            created_at=BASE_TIME - timedelta(days=87),
        ),
        Program(
            university_id=universities[1].id,
            name="Business",
            faculty="Economics",
            created_at=BASE_TIME - timedelta(days=86),
        ),
        Program(
            university_id=universities[1].id,
            name="Design",
            faculty="Arts",
            created_at=BASE_TIME - timedelta(days=85),
        ),
        Program(
            university_id=universities[2].id,
            name="Physics",
            faculty="Science",
            created_at=BASE_TIME - timedelta(days=84),
        ),
        Program(
            university_id=universities[2].id,
            name="Medicine",
            faculty="Health",
            created_at=BASE_TIME - timedelta(days=83),
        ),
    ]
    session.add_all(programs)
    session.flush()

    parent_categories = [
        Category(
            name="Academics",
            slug="academics",
            created_at=BASE_TIME - timedelta(days=78),
        ),
        Category(
            name="Campus Life",
            slug="campus-life",
            created_at=BASE_TIME - timedelta(days=77),
        ),
    ]
    session.add_all(parent_categories)
    session.flush()

    leaf_categories = [
        Category(
            parent_category_id=parent_categories[0].id,
            name="Books",
            slug="books",
            created_at=BASE_TIME - timedelta(days=76),
        ),
        Category(
            parent_category_id=parent_categories[0].id,
            name="Lab Gear",
            slug="lab-gear",
            created_at=BASE_TIME - timedelta(days=75),
        ),
        Category(
            parent_category_id=parent_categories[0].id,
            name="Electronics",
            slug="electronics",
            created_at=BASE_TIME - timedelta(days=74),
        ),
        Category(
            parent_category_id=parent_categories[1].id,
            name="Furniture",
            slug="furniture",
            created_at=BASE_TIME - timedelta(days=73),
        ),
        Category(
            parent_category_id=parent_categories[1].id,
            name="Fashion",
            slug="fashion",
            created_at=BASE_TIME - timedelta(days=72),
        ),
        Category(
            parent_category_id=parent_categories[1].id,
            name="Mobility",
            slug="mobility",
            created_at=BASE_TIME - timedelta(days=71),
        ),
    ]
    session.add_all(leaf_categories)
    session.flush()

    seller_names = [
        "Ana Seller",
        "Carlos Seller",
        "Daniela Seller",
        "Felipe Seller",
        "Laura Seller",
        "Mateo Seller",
        "Paula Seller",
        "Sara Seller",
    ]
    buyer_names = [
        "Luis Buyer",
        "Marta Buyer",
        "Camila Buyer",
        "Julian Buyer",
        "Valentina Buyer",
        "Andres Buyer",
        "Sofia Buyer",
        "Miguel Buyer",
        "Natalia Buyer",
        "Juan Buyer",
        "Maria Buyer",
        "Tomas Buyer",
    ]

    sellers: list[User] = []
    buyers: list[User] = []

    for index, name in enumerate(seller_names):
        university = universities[index % len(universities)]
        program = programs[index % len(programs)]
        seller = auth_service.signup(
            name=name,
            email=f"seller{index + 1}@example.com",
            password="secret123",
            university_id=university.id,
            program_id=program.id,
            is_verified=True,
            student_code=f"SELL{index + 1:03d}",
        )
        seller.created_at = BASE_TIME - timedelta(days=65 - index * 3)
        sellers.append(seller)

    for index, name in enumerate(buyer_names):
        university = universities[(index + 1) % len(universities)]
        program = programs[(index + 2) % len(programs)]
        buyer = auth_service.signup(
            name=name,
            email=f"buyer{index + 1}@example.com",
            password="secret123",
            university_id=university.id,
            program_id=program.id,
            is_verified=index % 3 != 0,
            student_code=f"BUY{index + 1:03d}",
        )
        buyer.created_at = BASE_TIME - timedelta(days=58 - index * 2)
        buyers.append(buyer)

    all_users = sellers + buyers
    for index, user in enumerate(all_users):
        login_times: list[datetime] = []
        for login_index in range(4):
            login_time = max(
                user.created_at + timedelta(hours=6 + login_index),
                BASE_TIME - timedelta(days=18) + timedelta(days=index + login_index * 9),
            )
            session.add(
                _create_activity(
                    user_id=user.id,
                    event_type="login",
                    created_at=login_time,
                )
            )
            login_times.append(login_time)
        user.last_login_at = max(login_times)
        session.add(user)

    listing_blueprints = {
        "books": [
            ("Calculus Notes", "Complete set of notes", "notes", "used", Decimal("45000"), True, True),
            ("Microeconomics Guide", "Annotated textbook and exercises", "book", "used", Decimal("68000"), False, False),
            ("Linear Algebra Cheatsheets", "Printed summaries for exams", "study-material", "new", Decimal("32000"), True, True),
        ],
        "lab-gear": [
            ("Chemistry Goggles", "Protective goggles for lab sessions", "accessory", "used", Decimal("38000"), False, True),
            ("Physics Lab Kit", "Sensors and components for experiments", "kit", "used", Decimal("145000"), False, False),
            ("White Lab Coat", "Medium size, almost new", "clothing", "used", Decimal("52000"), False, True),
        ],
        "electronics": [
            ("Scientific Calculator", "Approved for engineering exams", "device", "used", Decimal("125000"), False, False),
            ("Tablet for Notes", "10-inch tablet for classes", "device", "used", Decimal("420000"), False, True),
            ("Noise Cancelling Headphones", "Great for library sessions", "device", "used", Decimal("210000"), False, True),
        ],
        "furniture": [
            ("Dorm Desk Chair", "Compact ergonomic chair", "furniture", "used", Decimal("165000"), False, True),
            ("Study Lamp", "LED lamp with adjustable neck", "furniture", "new", Decimal("72000"), False, False),
            ("Bookshelf", "Small bookshelf for dorm rooms", "furniture", "used", Decimal("185000"), False, True),
        ],
        "fashion": [
            ("Uni Hoodie", "Official campus hoodie", "clothing", "used", Decimal("90000"), False, True),
            ("Rain Jacket", "Perfect for commuting to campus", "clothing", "used", Decimal("110000"), False, True),
            ("Sneakers", "Comfortable shoes for long days", "clothing", "used", Decimal("135000"), False, False),
        ],
        "mobility": [
            ("Campus Bike", "Single-speed bike in good condition", "vehicle", "used", Decimal("480000"), False, True),
            ("Electric Scooter", "Good battery life for short commutes", "vehicle", "used", Decimal("890000"), False, True),
            ("Skateboard", "Cruiser board for around campus", "vehicle", "used", Decimal("160000"), False, True),
        ],
    }
    search_terms = {
        "books": ["calculus notes", "economics textbook", "exam summary"],
        "lab-gear": ["lab coat", "goggles", "physics kit"],
        "electronics": ["calculator", "tablet", "headphones"],
        "furniture": ["desk chair", "study lamp", "bookshelf"],
        "fashion": ["hoodie", "jacket", "sneakers"],
        "mobility": ["bike", "scooter", "skateboard"],
    }
    campus_points = [
        "ML Building",
        "W Building",
        "Central Plaza",
        "Library Entrance",
        "Engineering Hall",
        "North Gate",
    ]

    total_listings = 36
    for listing_index in range(total_listings):
        seller = sellers[listing_index % len(sellers)]
        category = leaf_categories[listing_index % len(leaf_categories)]
        blueprint = listing_blueprints[category.slug][
            listing_index % len(listing_blueprints[category.slug])
        ]
        created_at = BASE_TIME + timedelta(
            days=listing_index,
            hours=(listing_index % 4) * 3,
        )
        published_at = created_at + timedelta(hours=1)
        price = blueprint[4] + Decimal((listing_index % 5) * 7000 + (listing_index // 6) * 3000)

        listing = Listing(
            seller_id=seller.id,
            category_id=category.id,
            title=blueprint[0],
            description=blueprint[1],
            product_type=blueprint[2],
            condition=blueprint[3],
            price=price,
            currency="COP",
            status="active",
            is_negotiable=blueprint[6],
            is_digital=blueprint[5],
            quantity_available=1,
            campus_pickup_point=campus_points[listing_index % len(campus_points)],
            created_at=created_at,
            published_at=published_at,
        )
        session.add(listing)
        session.flush()

        for media_index in range(1 + (listing_index % 2)):
            session.add(
                ListingMedia(
                    listing_id=listing.id,
                    asset_url=f"https://example.com/assets/{category.slug}-{listing_index + 1}-{media_index + 1}.png",
                    media_type="image",
                    sort_order=media_index,
                    created_at=published_at + timedelta(minutes=10 * (media_index + 1)),
                )
            )

        session.add(
            ListingStatusHistory(
                listing_id=listing.id,
                changed_by_user_id=seller.id,
                from_status=None,
                to_status="active",
                changed_at=published_at,
            )
        )
        session.add(
            _create_activity(
                user_id=seller.id,
                event_type="listing_created",
                created_at=published_at,
                listing_id=listing.id,
            )
        )

        for search_index in range(2 + (listing_index % 3)):
            search_user = buyers[(listing_index + search_index * 2) % len(buyers)]
            search_time = created_at + timedelta(hours=2 + search_index * 5)
            search_event = SearchEvent(
                user_id=search_user.id,
                category_id=category.id,
                query_text=search_terms[category.slug][search_index % len(search_terms[category.slug])],
                sort_mode=("recent", "price_asc", "relevance")[search_index % 3],
                results_count=3 + ((listing_index + search_index) % 6),
                created_at=search_time,
            )
            session.add(search_event)
            session.add(
                _create_activity(
                    user_id=search_user.id,
                    event_type="search",
                    created_at=search_time,
                )
            )

        interested_buyers = [
            buyers[(listing_index * 2) % len(buyers)],
            buyers[(listing_index * 2 + 5) % len(buyers)],
        ]
        thread_total = 1 + (listing_index % 3 != 1)
        for thread_index in range(thread_total):
            buyer = interested_buyers[thread_index]
            thread_time = created_at + timedelta(hours=6 + thread_index * 3)
            thread = MessageThread(
                listing_id=listing.id,
                buyer_id=buyer.id,
                seller_id=seller.id,
                created_at=thread_time,
            )
            session.add(thread)
            session.flush()

            last_message_at = thread_time
            message_total = 2 + ((listing_index + thread_index) % 3)
            for message_index in range(message_total):
                sender = buyer if message_index % 2 == 0 else seller
                message_time = thread_time + timedelta(hours=message_index * 4)
                message = Message(
                    thread_id=thread.id,
                    sender_id=sender.id,
                    body=(
                        f"Interested in {listing.title.lower()} - message {message_index + 1}"
                        if sender.id == buyer.id
                        else f"Reply about {listing.title.lower()} - message {message_index + 1}"
                    ),
                    is_read=message_index < message_total - 1,
                    created_at=message_time,
                )
                session.add(message)
                session.add(
                    _create_activity(
                        user_id=sender.id,
                        event_type="message",
                        created_at=message_time,
                        listing_id=listing.id,
                    )
                )
                last_message_at = message_time

            thread.last_message_at = last_message_at
            session.add(thread)

        transaction_buyer = interested_buyers[0]
        transaction_created_at = created_at + timedelta(days=1 + (listing_index % 3), hours=2)
        agreed_price = price - Decimal((listing_index % 4) * 2500) if listing.is_negotiable else price
        outcome = listing_index % 5

        transaction = MarketplaceTransaction(
            listing_id=listing.id,
            buyer_id=transaction_buyer.id,
            seller_id=seller.id,
            listed_price=price,
            agreed_price=agreed_price,
            currency="COP",
            status="pending",
            created_at=transaction_created_at,
        )
        session.add(transaction)
        session.flush()

        session.add(
            _create_activity(
                user_id=transaction_buyer.id,
                event_type="transaction",
                created_at=transaction_created_at,
                listing_id=listing.id,
                transaction_id=transaction.id,
            )
        )

        if outcome in {0, 1, 2}:
            completed_at = transaction_created_at + timedelta(hours=10 + (listing_index % 8))
            transaction.status = "completed"
            transaction.completed_at = completed_at
            listing.status = "sold"
            listing.sold_at = completed_at
            session.add(
                ListingStatusHistory(
                    listing_id=listing.id,
                    changed_by_user_id=seller.id,
                    from_status="active",
                    to_status="sold",
                    changed_at=completed_at,
                )
            )
            session.add(
                _create_activity(
                    user_id=seller.id,
                    event_type="transaction",
                    created_at=completed_at,
                    listing_id=listing.id,
                    transaction_id=transaction.id,
                )
            )

            rating = 5 if listing_index % 4 != 0 else 4
            review_time = completed_at + timedelta(hours=4 + (listing_index % 5))
            session.add(
                Review(
                    transaction_id=transaction.id,
                    reviewer_id=transaction_buyer.id,
                    reviewee_id=seller.id,
                    rating=rating,
                    comment=f"Great experience buying {listing.title.lower()}",
                    created_at=review_time,
                )
            )
            seller_ratings[seller.id].append(rating)
        elif outcome == 3:
            cancelled_at = transaction_created_at + timedelta(hours=8)
            transaction.status = "cancelled"
            transaction.cancelled_at = cancelled_at
            session.add(
                _create_activity(
                    user_id=transaction_buyer.id,
                    event_type="transaction",
                    created_at=cancelled_at,
                    listing_id=listing.id,
                    transaction_id=transaction.id,
                )
            )
            if listing_index % 2 == 0:
                archived_at = cancelled_at + timedelta(days=5)
                listing.status = "archived"
                listing.archived_at = archived_at
                session.add(
                    ListingStatusHistory(
                        listing_id=listing.id,
                        changed_by_user_id=seller.id,
                        from_status="active",
                        to_status="archived",
                        changed_at=archived_at,
                    )
                )

        session.add(transaction)
        session.add(listing)

    for seller in sellers:
        ratings = seller_ratings[seller.id]
        seller.rating = round(sum(ratings) / len(ratings)) if ratings else 4
        session.add(seller)

    session.commit()


def seed_sample_data(session: Session | None = None) -> None:
    if session is not None:
        _seed_sample_data(session)
        return

    engine = get_engine()
    with Session(engine) as managed_session:
        _seed_sample_data(managed_session)


if __name__ == "__main__":
    Path("viz/output").mkdir(parents=True, exist_ok=True)
    seed_sample_data()
