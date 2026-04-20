from datetime import UTC, datetime
from uuid import uuid7

from sqlmodel import Session, select

from marketplace_andes.categories.models import Category


def test_delete_all_categories(get_test_client, get_db_test_session: Session):
    existing_count = len(get_db_test_session.exec(select(Category)).all())
    now = datetime.now(UTC)
    first_category = Category(
        id=uuid7(),
        name="test-delete-categories-1",
        created_at=now,
        updated_at=now,
    )
    second_category = Category(
        id=uuid7(),
        name="test-delete-categories-2",
        created_at=now,
        updated_at=now,
    )
    get_db_test_session.add(first_category)
    get_db_test_session.add(second_category)
    get_db_test_session.commit()

    response = get_test_client.delete("/categories")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": existing_count + 2}
    assert get_db_test_session.exec(select(Category)).all() == []
