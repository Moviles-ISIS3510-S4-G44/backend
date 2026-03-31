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

if [[ -z "${ANALYTICS_PASSWORD:-}" ]]; then
    echo "Missing required env var: ANALYTICS_PASSWORD" >&2
    exit 1
fi

psql -v ON_ERROR_STOP=1 \
--username "$POSTGRES_USER" \
--dbname "$POSTGRES_DB" \
-v backend_password="$BACKEND_PASSWORD" \
-v backend_migration_password="$BACKEND_MIGRATION_PASSWORD" \
-v analytics_password="$ANALYTICS_PASSWORD" <<-EOSQL
    -- user creation
    CREATE USER backend_user WITH PASSWORD :'backend_password';
    CREATE USER backend_migration_user WITH PASSWORD :'backend_migration_password';
    CREATE USER analytics_user WITH PASSWORD :'analytics_password';

    -- db creation
    CREATE DATABASE marketplace;

    \c marketplace

    GRANT CONNECT ON DATABASE marketplace TO backend_user;
    GRANT CONNECT ON DATABASE marketplace TO backend_migration_user;
    GRANT CONNECT ON DATABASE marketplace TO analytics_user;

    -- Lock down schema creation to migration role only.
    REVOKE CREATE ON SCHEMA public FROM PUBLIC;

    -- App role: data CRUD only.
    GRANT USAGE ON SCHEMA public TO backend_user;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO backend_user;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO backend_user;

    -- Migration role: schema/object management privileges.
    GRANT USAGE, CREATE ON SCHEMA public TO backend_migration_user;

     -- Analytics role: read-only access.
    GRANT USAGE ON SCHEMA public TO analytics_user;
    GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_user;

    -- Ensure future migration-created objects are usable by app role.
    ALTER DEFAULT PRIVILEGES FOR USER backend_migration_user IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO backend_user;
    ALTER DEFAULT PRIVILEGES FOR USER backend_migration_user IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO backend_user;

    -- Ensure future tables are readable by analytics role.
    ALTER DEFAULT PRIVILEGES FOR USER backend_migration_user IN SCHEMA public
        GRANT SELECT ON TABLES TO analytics_user;
EOSQL
