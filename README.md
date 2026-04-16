# Marketplace Andes Backend

[![CI](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/ci.yaml/badge.svg)](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/ci.yaml)

> I'm sorry, Dave. I'm afraid I can't do that

## How to

## Submit changes in github

Create an PR with the changes you want to perform to `master`

**NOTE: only do this when the feature branch is COMPLETE and you want to merge with master"

Then when it is ready perform an rebase with

```bash
git checkout <feature-branch>
git rebase master
```

Probably this will as you to `git push -f` to your feature branch

> This will make your changes atop the latest master commit

Then in the PR preferably use (**This isnt an option :D**) `squash`

## Create an migration

Go to `migrations`

And run

```bash
uv run alembic revision -m <message>
```

Then in `schema` folder there must be an new file that you can edit
for the migration

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

There are several Docker Compose `profiles`:

- `migrations`: executes DB migrations.
- `load_fake`: loads initial fake data (users, profiles and listings).
- `pgadmin`: starts pgAdmin UI.

### Run initial fake data (`load_fake`)

Use profiles to run migrations and fake data load in one flow:

```bash
docker compose --profile migrations --profile load_fake up --build migration load_fake
```

If you also want the API running at the same time:

```bash
docker compose --profile migrations --profile load_fake up --build
```

To reset DB state and run from scratch:

```bash
docker compose down -v
docker compose --profile migrations --profile load_fake up --build migration load_fake
```

## Run the analytics pipeline

`Requisites: uv, Bun and PostgreSQL with data (use migrations + load_fake first)`

1. Run ELT (`dlt` + `dbt`) from `analytics/dlt_pipeline`:

```bash
cd analytics/dlt_pipeline
uv sync
uv run load_data_pipeline.py
```

2. Run the reports app from `analytics/dbt/reports`:

```bash
cd analytics/dbt/reports
bun install
bun run sources
bun run dev
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
