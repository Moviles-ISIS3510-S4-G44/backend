# Project Guidelines

## Build And Test
- Always use `uv` for Python dependency and command execution in this repo.
- Ensure commands run inside the project virtual environment (`.venv`), via
`. .venv/bin/activate`.
- Preferred local setup: `uv sync --dev`
- Run the API locally: `docker compose up --build`
- Tear down containers and volumes: `docker compose down -v`
- Run tests: `uv run pytest`
- Run tests with coverage: `uv run pytest --cov`
- If compose fails due to missing env files, run: `for f in *.template; do cp -n "$f" "${f%.template}"; done`

## Architecture
- This is a FastAPI + SQLModel backend organized by domain under `src/marketplace_andes_backend/`.
- Main domains are:
  - `auth/`: signup, login, and JWT-based authentication
  - `users/` and `users/profile/`: user entities and profile endpoints
  - `health/`: health-check endpoints
- Typical flow is route -> service -> ORM model/session.
- Routers are composed in `src/marketplace_andes_backend/app.py`.

## Conventions
- Follow the existing dependency-injection style using `typing.Annotated` aliases (see `AuthServiceDep`, `CurrentUserDep`, and `SessionDep`).
- Keep business rules in service classes and keep route handlers thin.
- Raise domain exceptions in services and map them to `HTTPException` in routes.
- Keep schema/model responsibilities split:
  - SQLModel models define persistence concerns.
  - Pydantic schemas define request/response payloads.
- Keep API behavior and status codes consistent with existing route modules.

## Database And Migrations
- PostgreSQL is required for local/dev workflows.
- In Docker workflows, `server` waits for `migration` and healthy `postgres`.
- Alembic migrations live in `alembic/versions/`; create additive migrations and avoid rewriting existing revisions.

## Testing Conventions
- Prefer endpoint-level tests with `TestClient` and DB-backed fixtures from `tests/conftest.py`.
- Tests rely on a Postgres test container and run Alembic migrations before test execution.
- For DB tests, keep transactional fixture behavior intact (rollback-based isolation).

## Documentation Index
- Project setup and common commands: `README.md`
- App relational model notes: `docs/APP_DB_MODEL.md`
- Analytics definitions: `docs/ANALYTICS.md`
- Analytics star schema: `docs/ANALYTICS_STAR_MODEL.md`

## Agent Guardrails
- Prefer minimal, focused changes that match existing module boundaries and naming.
- Do not introduce new frameworks or architecture layers unless explicitly requested.
- When adding endpoints, mirror existing patterns in `auth/routes.py`, `users/routes.py`, and related service/schema files.