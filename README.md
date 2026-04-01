# Marketplace Andes Backend

[![CI](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/ci.yaml/badge.svg)](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/ci.yaml)

> I'm sorry, Dave. I'm afraid I can't do that

## How to

## Run the server

`Requisites: Docker`

> In short docker is in charge of getting the dependencies right and
> it will try (not try, will blatlantly do) to create identical
> environments for running the server
> So if you spin an VM in AWS, Azure, GCP and install docker without any other thing INSTALLED
> you should get the server running with an docker compose up :D

The server is orchestrated via `Docker Compose`, that ensures reproducibility

The default Compose workload will spin up the `backend server` and the `database`

But before this... **Really important**

Ensure you put the `.env.<name>.template` files from `env_templates`
in the root of the project without the `.template`

That is for `.env.server.template` put it into the root of the project as `.env.server`,
do the same for the rest of the files.

There is an helper script at `scripts/` folder

```bash
docker compose up --build
```

You can choose to run it detached with

```bash
docker compose up --build -d
```

And if you want to reflect the changes you make to the server in real time run

```bash
docker compose up --build --watch
```

Note: detach mode and watch cannot be used toguether

To tear down the project use:

```bash
docker compose down
```

If you want to delete volumes (Mostly if you want to delete database state use)

```bash
docker compose down -v
```

Mmmmm here is where the things get complicated

There are several Docker Compose `profiles`

- pgadmin (setups and graphical panel for postgres usable from the browser)
- migrations (performs db migrations)
- load_fake (well... loads the fake data, and happens after migrations)

You use it as:

```bash
docker compose --profile <x> --profile <y> ... <command>
```

So the command for doing an initial setup would be

```bash
docker compose --profile migrations --profile load_fake --profile pgadmin up --build --watch
```

and to tear down

```bash
docker compose --profile migrations --profile load_fake --profile pgadmin down -v
```

## Run the analytics pipeline

`Requisites: uv & Bun & How to run the server`

## 1. Run the ELT

This will run `dlt` (Data load tool) and `dbt` altogether

Go to `analytics/dlt_pipeline`

And run

```bash
uv run load_data_pipeline.py
```

Then go to `analytics/dbt/reports`

And run

```bash
bun run sources
bun run dev # this runs an server with the viz dashboard
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
