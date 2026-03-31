def test_register_user(get_test_client, get_tear_down_user):
    username = "test_register_user"
    password = "secret-pass"

    response = get_test_client.post(
        "/auth/register",
        json={"username": username, "password": password},
    )

    assert response.status_code == 201

    get_tear_down_user(response.json()["user_id"])


def test_login_user(get_test_client, get_test_user):
    user, _, password = get_test_user
    username = user.username

    response = get_test_client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )

    assert response.status_code == 200
