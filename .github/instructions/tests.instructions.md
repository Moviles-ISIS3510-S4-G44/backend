---
description: "Use when writing or updating pytest tests, FastAPI endpoint tests, fixtures, or test database setup in this repository. Covers fixture usage, auth patterns, and uv-based test execution."
name: "Backend Testing Guidelines"
applyTo: "tests/**/*.py"
---
# Testing Guidelines

- Always use `uv` for Python commands.
- Ensure commands run inside the project virtual environment (`.venv`), preferably with `uv run <command>`.
- Run tests with `uv run pytest`.
- Run coverage with `uv run pytest --cov`.

## Scope And Style

- Prefer endpoint-level tests with `fastapi.testclient.TestClient` over direct unit tests of route internals.
- Keep assertions behavior-focused: status code, response payload, and key persisted DB effects.
- Keep test names explicit and scenario-based (`test_<action>_<expected_outcome>`).

## Fixtures And DB Usage

- Reuse fixtures from `tests/conftest.py` (`client`, `session`) instead of creating ad-hoc app/session setup.
- Preserve transactional isolation by using the provided `session` fixture and avoiding global DB state.
- For authenticated endpoints, use fixture helpers to create users/tokens via existing auth service patterns.

## Error And Edge Cases

- For new endpoints, include at least one success case and one failure case.
- Cover auth behavior explicitly for protected routes (`401` without token, invalid token path when relevant).
- Keep status-code expectations aligned with existing route behavior.

## Keep In Sync

- If an endpoint contract changes (schema, status code, auth requirement), update tests in the same change.
- Prefer small, focused test additions near related domain tests (`tests/auth/`, `tests/users/`).
