# Marketplace Andes Backend

[![CI](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/ci.yaml/badge.svg)](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/ci.yaml)

## Commands

```bash
docker compose --profile dev --profile load_fake --profile pgadmin up --build
docker compose --profile dev --profile pgadmin up --build --watch
docker compose --profile dev --profile pgadmin down -v
```

## Learning

When doint commits on the session, it expires. And subsequent accesses to it
may trigger additional SQL queries.

In my case it was

```python
    def register_user(self, username: str, password: str, anon_ip: str) -> UUID:
        if self.__user_repository.get_id_from_username(username):
            self.__logger.warning(
                f"Registration attempted with existing username: {username} at IP: {anon_ip}"
            )
            raise DuplicateUserError("Username already exists")

        user = self.__user_repository.create_user(username)
        self.__session.flush()

        self.__auth_repository.create_auth_user(
            user.id, self.__password_hasher.hash(password)
        )
        self.__session.commit()
        self.__logger.info(
            f"User: {username} registered successfully with id: {user.id} at IP: {anon_ip}"
        )
        return user.id
```

So in short if retrieved data from DB save it to an DTO.
And dont use the SQLModel entity object.
