---
description: "Create a new FastAPI endpoint in this backend, including route, service logic, schemas, tests, and migration updates when needed."
name: "Create New Endpoint"
argument-hint: "Describe method, path, auth requirement, request body, response shape, validation rules, and error cases"
agent: "agent"
---
Implement a new backend endpoint from the request in chat.

Use this repository style and file patterns:
- [App router composition](../../src/marketplace_andes_backend/app.py)
- [Auth routes pattern](../../src/marketplace_andes_backend/auth/routes.py)
- [Auth service pattern](../../src/marketplace_andes_backend/auth/service.py)
- [User routes pattern](../../src/marketplace_andes_backend/users/routes.py)
- [Profile routes pattern](../../src/marketplace_andes_backend/users/profile/routes.py)
- [Test fixtures](../../tests/conftest.py)
- [Auth tests](../../tests/auth/test_auth.py)

Requirements:
1. Keep route handlers thin and move business logic to service classes.
2. Follow dependency injection style with typing.Annotated aliases.
3. Map domain exceptions to HTTPException in routes.
4. Keep SQLModel models and request/response schemas separated.
5. Preserve existing status code and error message conventions.
6. Always use uv for Python commands and ensure execution in .venv.

Deliverables:
1. Implement endpoint code in the correct domain module(s).
2. Add or update endpoint tests under tests/ with success and failure cases.
3. If persistence changes are required, add an additive Alembic migration in alembic/versions/.
4. Update imports/router wiring when needed.
5. Run relevant verification commands and report results.

Verification commands:
- uv run pytest
- uv run pytest --cov

Final response format:
1. Summary of behavior added.
2. Files changed and why.
3. Test results.
4. Follow-up risks or assumptions.
