---
description: "Use when writing or updating Alembic migration files, migration environment code, or schema changes for PostgreSQL in this repository. Covers additive migrations, rollback safety, and uv-based execution."
name: "Migration Guidelines"
applyTo: "alembic/**/*.py"
---
# Migration Guidelines

- Always use `uv` for Python commands.
- Ensure commands run inside the project virtual environment (`.venv`), via `. .venv/bin/activate`.
- Run migrations with `uv run alembic upgrade head`.

## Safety Rules

- Create additive migrations; do not rewrite existing revision files.
- Keep each migration focused on one logical change.
- Prefer expand-then-migrate-then-contract patterns for breaking schema changes.
- Avoid destructive operations (drop/rename/type narrowing) unless explicitly required.

## Revision Practices

- Every migration must define `revision`, `down_revision`, `upgrade()`, and `downgrade()`.
- Keep `downgrade()` implemented and reversible when feasible.
- Use clear, deterministic operations in `upgrade()` and `downgrade()`.

## Repo-Specific Expectations

- Migration files live in `alembic/versions/`.
- Keep migration behavior compatible with Docker flow where `server` depends on successful `migration` completion.
- Do not introduce data backfills in startup paths; keep data migrations explicit and bounded.

## Validation

- Validate migration ordering and dependencies before committing.
- When changing ORM models, include migration updates in the same change.
- Keep changes aligned with existing SQLModel/Alembic patterns in this repository.
