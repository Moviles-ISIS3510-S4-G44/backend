from decimal import Decimal

from sqlmodel import Session, delete, select

from src.marketplace_andes_backend.categories.models import Category
from src.marketplace_andes_backend.db import get_engine
from src.marketplace_andes_backend.listings.models import Listing
from src.marketplace_andes_backend.users.models import User

REQUIRED_USERS: tuple[dict[str, str | int], ...] = (
    {"name": "Diego", "email": "diego@marketplace.test", "rating": 5},
    {"name": "Maria Camila", "email": "maria.camila@marketplace.test", "rating": 5},
    {"name": "Yesid", "email": "yesid@marketplace.test", "rating": 4},
    {"name": "Isaac", "email": "isaac@marketplace.test", "rating": 4},
    {"name": "Santiago", "email": "santiago@marketplace.test", "rating": 5},
    {"name": "Louise", "email": "louise@marketplace.test", "rating": 4},
)

REQUIRED_CATEGORIES: tuple[str, ...] = ("Books", "Electronics", "Furniture")

REQUIRED_LISTINGS: tuple[dict[str, str | Decimal], ...] = (
    {
        "seller_email": "diego@marketplace.test",
        "category_name": "Electronics",
        "title": "iPhone 14 Pro 256GB",
        "description": "Unlocked, 91% battery health, incluye cargador.",
        "price": Decimal("3300.00"),
        "condition": "used",
        "images": '["https://example.com/images/iphone14pro.jpg"]',
        "status": "active",
        "location": "Bogotá",
    },
    {
        "seller_email": "maria.camila@marketplace.test",
        "category_name": "Books",
        "title": "Cien años de soledad - edición de colección",
        "description": "Tapa dura, excelente estado, sin anotaciones.",
        "price": Decimal("85000.00"),
        "condition": "used",
        "images": '["https://example.com/images/cien-anos.jpg"]',
        "status": "active",
        "location": "Medellín",
    },
    {
        "seller_email": "yesid@marketplace.test",
        "category_name": "Furniture",
        "title": "Escritorio en madera de roble",
        "description": "140x70 cm, ideal para home office.",
        "price": Decimal("420000.00"),
        "condition": "used",
        "images": '["https://example.com/images/escritorio-roble.jpg"]',
        "status": "active",
        "location": "Cali",
    },
    {
        "seller_email": "isaac@marketplace.test",
        "category_name": "Electronics",
        "title": "Monitor LG UltraWide 29 pulgadas",
        "description": "Resolución Full HD, perfecto para productividad.",
        "price": Decimal("760000.00"),
        "condition": "used",
        "images": '["https://example.com/images/lg-ultrawide.jpg"]',
        "status": "active",
        "location": "Barranquilla",
    },
    {
        "seller_email": "santiago@marketplace.test",
        "category_name": "Furniture",
        "title": "Silla ergonómica para oficina",
        "description": "Soporte lumbar ajustable y reposabrazos 3D.",
        "price": Decimal("390000.00"),
        "condition": "used",
        "images": '["https://example.com/images/silla-ergonomica.jpg"]',
        "status": "active",
        "location": "Bucaramanga",
    },
    {
        "seller_email": "louise@marketplace.test",
        "category_name": "Books",
        "title": "Clean Code en español",
        "description": "Libro de ingeniería de software, como nuevo.",
        "price": Decimal("120000.00"),
        "condition": "new",
        "images": '["https://example.com/images/clean-code.jpg"]',
        "status": "active",
        "location": "Cartagena",
    },
    {
        "seller_email": "diego@marketplace.test",
        "category_name": "Electronics",
        "title": "Teclado mecánico Keychron K2",
        "description": "Switches brown, conexión Bluetooth y USB-C.",
        "price": Decimal("280000.00"),
        "condition": "used",
        "images": '["https://example.com/images/keychron-k2.jpg"]',
        "status": "active",
        "location": "Bogotá",
    },
    {
        "seller_email": "maria.camila@marketplace.test",
        "category_name": "Furniture",
        "title": "Lámpara de pie minimalista",
        "description": "Luz cálida regulable, base metálica negra.",
        "price": Decimal("160000.00"),
        "condition": "new",
        "images": '["https://example.com/images/lampara-pie.jpg"]',
        "status": "active",
        "location": "Medellín",
    },
    {
        "seller_email": "yesid@marketplace.test",
        "category_name": "Books",
        "title": "The Pragmatic Programmer",
        "description": "Edición 20 aniversario en inglés.",
        "price": Decimal("145000.00"),
        "condition": "used",
        "images": '["https://example.com/images/pragmatic-programmer.jpg"]',
        "status": "active",
        "location": "Cali",
    },
)


def seed_database(session: Session) -> None:
    users_by_email: dict[str, User] = {}
    for user_data in REQUIRED_USERS:
        email = str(user_data["email"])
        user = session.exec(select(User).where(User.email == email)).first()
        if user is None:
            user = User(
                name=str(user_data["name"]),
                email=email,
                rating=int(user_data["rating"]),
            )
            session.add(user)
            session.flush()
        else:
            user.name = str(user_data["name"])
            user.rating = int(user_data["rating"])
        users_by_email[email] = user

    categories_by_name: dict[str, Category] = {}
    for category_name in REQUIRED_CATEGORIES:
        category = session.exec(
            select(Category).where(Category.name == category_name)
        ).first()
        if category is None:
            category = Category(name=category_name)
            session.add(category)
            session.flush()
        categories_by_name[category_name] = category

    for listing_data in REQUIRED_LISTINGS:
        seller = users_by_email[str(listing_data["seller_email"])]
        category = categories_by_name[str(listing_data["category_name"])]
        statement = select(Listing).where(
            Listing.seller_id == seller.id,
            Listing.category_id == category.id,
            Listing.title == str(listing_data["title"]),
        )
        listing = session.exec(statement).first()
        if listing is None:
            listing = Listing(
                seller_id=int(seller.id),
                category_id=int(category.id),
                title=str(listing_data["title"]),
                description=str(listing_data["description"]),
                price=Decimal(str(listing_data["price"])),
                condition=str(listing_data["condition"]),
                images=str(listing_data["images"]),
                status=str(listing_data["status"]),
                location=str(listing_data["location"]),
            )
            session.add(listing)
            continue

        listing.description = str(listing_data["description"])
        listing.price = Decimal(str(listing_data["price"]))
        listing.condition = str(listing_data["condition"])
        listing.images = str(listing_data["images"])
        listing.status = str(listing_data["status"])
        listing.location = str(listing_data["location"])

    session.commit()


def clear_database(session: Session) -> None:
    session.exec(delete(Listing))
    session.exec(delete(Category))
    session.exec(delete(User))
    session.commit()


def run_seed_database() -> None:
    with Session(get_engine()) as session:
        seed_database(session)


def run_clear_database() -> None:
    with Session(get_engine()) as session:
        clear_database(session)
