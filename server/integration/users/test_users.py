from datetime import UTC, datetime
from uuid import uuid7

from sqlmodel import Session, select

from marketplace_andes.auth.session.models import AuthSession
from marketplace_andes.users.models import User


def test_delete_all_users(
    get_test_client, get_db_test_session: Session, get_setup_user
):
    username = "test-delete-users-auth"
    password = "secret-pass"
    user, _ = get_setup_user(username, password)

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

    users_before_deletion = len(get_db_test_session.exec(select(User)).all())
    login_response = get_test_client.post(
        "/auth/login",
        data={"username": user.username, "password": password},
    )

    assert login_response.status_code == 200

    response = get_test_client.delete(
        "/user",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json() == {"deleted_count": users_before_deletion}
    assert get_db_test_session.exec(select(User)).all() == []
    assert get_db_test_session.exec(select(AuthSession)).all() == []
