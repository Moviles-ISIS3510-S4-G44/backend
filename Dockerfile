FROM ghcr.io/astral-sh/uv:0.10.6-python3.14-trixie-slim AS builder

ENV UVICORN_WORKERS=1

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV UV_NO_DEV=1
ENV UV_PYTHON_INSTALL_DIR=/python
ENV UV_PYTHON_PREFERENCE=only-managed

RUN uv python install 3.14

WORKDIR /app

RUN --mount=type=cache,target=/root/.cache/uv \
--mount=type=bind,source=uv.lock,target=uv.lock \
--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
uv sync --locked --no-install-project

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
uv sync --locked

FROM debian:trixie-slim

RUN groupadd --system --gid 999 nonroot \
&& useradd --system --gid 999 --uid 999 --create-home nonroot

COPY --from=builder --chown=python:python /python /python

COPY --from=builder --chown=nonroot:nonroot /app /app

ENV PATH="/app/.venv/bin:$PATH"

USER nonroot

WORKDIR /app

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "src/backend/app.py"]