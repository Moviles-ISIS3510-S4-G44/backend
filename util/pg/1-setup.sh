#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${BACKEND_PASSWORD:-}" ]]; then
    echo "Missing required env var: BACKEND_PASSWORD" >&2
    exit 1
fi

if [[ -z "${BACKEND_MIGRATION_PASSWORD:-}" ]]; then
    echo "Missing required env var: BACKEND_MIGRATION_PASSWORD" >&2
    exit 1
fi

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -v backend_password="$BACKEND_PASSWORD" -v backend_migration_password="$BACKEND_MIGRATION_PASSWORD" <<-EOSQL
    CREATE USER backend_user WITH PASSWORD :'backend_password';
    CREATE USER backend_migration_user WITH PASSWORD :'backend_migration_password';

    CREATE DATABASE marketplace;

    \c marketplace

    GRANT CONNECT ON DATABASE marketplace TO backend_user;
    GRANT CONNECT ON DATABASE marketplace TO backend_migration_user;

    -- Lock down schema creation to migration role only.
    REVOKE CREATE ON SCHEMA public FROM PUBLIC;

    -- App role: data CRUD only.
    GRANT USAGE ON SCHEMA public TO backend_user;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO backend_user;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO backend_user;

    -- Migration role: schema/object management privileges.
    GRANT USAGE, CREATE ON SCHEMA public TO backend_migration_user;

    -- Ensure future migration-created objects are usable by app role.
    ALTER DEFAULT PRIVILEGES FOR USER backend_migration_user IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO backend_user;
    ALTER DEFAULT PRIVILEGES FOR USER backend_migration_user IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO backend_user;

EOSQL
