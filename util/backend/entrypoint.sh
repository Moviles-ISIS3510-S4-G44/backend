#!/usr/bin/env bash
set -euo pipefail

fastapi run --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}
