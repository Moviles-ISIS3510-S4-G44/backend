from datetime import UTC, datetime
from uuid import uuid7

from sqlmodel import Session, delete, select

from marketplace_andes.categories.models import Category
from marketplace_andes.listings.enums import ListingCondition
from marketplace_andes.listings.models import Listing
from marketplace_andes.users.models import User


def test_delete_all_listings(get_test_client, get_db_test_session: Session):
    now = datetime.now(UTC)
    category = Category(id=uuid7(), name="test-category", created_at=now, updated_at=now)
    first_user = User(
        id=uuid7(),
        username="test-delete-listings-user-1",
        created_at=now,
        updated_at=now,
    )
    second_user = User(
        id=uuid7(),
        username="test-delete-listings-user-2",
        created_at=now,
        updated_at=now,
    )
    first_listing = Listing(
        id=uuid7(),
        seller_id=first_user.id,
        category_id=category.id,
        title="first listing",
        description="first listing description",
        price=1000,
        condition=ListingCondition.USED,
        images=["https://example.com/1.png"],
        location="Bogota",
        status="draft",
        created_at=now,
        updated_at=now,
    )
    second_listing = Listing(
        id=uuid7(),
        seller_id=second_user.id,
        category_id=category.id,
        title="second listing",
        description="second listing description",
        price=2000,
        condition=ListingCondition.NEW,
        images=["https://example.com/2.png"],
        location="Medellin",
        status="draft",
        created_at=now,
        updated_at=now,
    )

    get_db_test_session.add(category)
    get_db_test_session.add(first_user)
    get_db_test_session.add(second_user)
    get_db_test_session.add(first_listing)
    get_db_test_session.add(second_listing)
    get_db_test_session.commit()

    response = get_test_client.delete("/listings")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": 2}
    assert get_db_test_session.exec(select(Listing)).all() == []

    get_db_test_session.exec(delete(Category).where(Category.id == category.id))
    get_db_test_session.exec(delete(User).where(User.id == first_user.id))
    get_db_test_session.exec(delete(User).where(User.id == second_user.id))
    get_db_test_session.commit()
