#!/usr/bin/env bash
set -euo pipefail

if [[ "${RUN_MIGRATIONS:-0}" == "1" ]]; then
    alembic upgrade head
else
    echo "RUN_MIGRATIONS is disabled, skipping migrations."
fi