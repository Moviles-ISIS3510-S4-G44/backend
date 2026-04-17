from datetime import UTC, datetime
from uuid import uuid7

from sqlmodel import Session, select

from marketplace_andes.users.models import User


def test_delete_all_users(get_test_client, get_db_test_session: Session):
    before_count = len(get_db_test_session.exec(select(User)).all())
    now = datetime.now(UTC)

    first_user = User(
        id=uuid7(),
        username="test-delete-users-1",
        created_at=now,
        updated_at=now,
    )
    second_user = User(
        id=uuid7(),
        username="test-delete-users-2",
        created_at=now,
        updated_at=now,
    )

    get_db_test_session.add(first_user)
    get_db_test_session.add(second_user)
    get_db_test_session.commit()

    response = get_test_client.delete("/user")

    assert response.status_code == 200
    assert response.json() == {"deleted_count": before_count + 2}
    assert get_db_test_session.exec(select(User)).all() == []
