#!/usr/bin/env bash
set -e

BACKEND_PASSWORD_FILE="/run/secrets/pg-backend-password"

if [[ ! -f "$BACKEND_PASSWORD_FILE" ]]; then
    echo "Missing secret file: $BACKEND_PASSWORD_FILE" >&2
    exit 1
fi

BACKEND_PASSWORD="$(<"$BACKEND_PASSWORD_FILE")"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -v backend_password="$BACKEND_PASSWORD" <<-EOSQL
    CREATE USER backend_user WITH PASSWORD :'backend_password';
    CREATE DATABASE marketplace;
    GRANT ALL PRIVILEGES ON DATABASE marketplace TO backend_user;
EOSQL
