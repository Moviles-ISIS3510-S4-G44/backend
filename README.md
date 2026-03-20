# Marketplace Andes Backend

[![Backend CI](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/backend-ci.yaml/badge.svg)](https://github.com/Moviles-ISIS3510-S4-G44/backend/actions/workflows/backend-ci.yaml)

## Useful Commands

```bash
uv run viz/run_pipeline.py
```

```bash
docker compose up --build
docker compose down -v

# with pgadmin
docker compose --profile pgadmin up --build
docker compose --profile pgadmin down -v
```

```bash
pytest
```

```bash
alembic upgrade head
```

```bash
docker stop $(docker ps -aq)
```

```bash
gh pr create --base main \
--head <branch> \
--title "feat(xxx): XXX" \
--body "Closes <#xxxx>"

# example
#gh pr create --base master --head orpheezt/feat/user-domain --title "feat(user): introduce User API" --body "Closes #123"
```

## Notes

### env files

For use docker compose you need env files

run

```bash
for f in *.template; do cp -n "$f" "${f%.template}"; done
```
