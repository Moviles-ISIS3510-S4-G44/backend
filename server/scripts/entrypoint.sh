#!/usr/bin/env bash
set -euo pipefail

fastapi run --entrypoint marketplace_andes.app:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}