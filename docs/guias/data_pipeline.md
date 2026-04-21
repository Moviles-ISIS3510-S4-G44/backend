# Guía del data pipeline

Esta guía explica cómo ejecutar el pipeline de datos y cómo está compuesto su flujo dentro del repositorio.

## 1. ¿Qué componentes participan?

- **Backend + PostgreSQL (OLTP):** origen de los datos transaccionales.
- **`load_fake`:** carga datos sintéticos para pruebas/demo.
- **`analytics/dlt_pipeline`:** capa ELT en Python que ejecuta:
  - extracción/carga con **dlt** desde PostgreSQL,
  - transformación con **dbt**.
- **DuckDB (`analytics.duckdb`):** almacenamiento analítico local.
- **Evidence (`analytics/dbt/reports`):** capa de visualización/reportes.

## 2. Flujo del pipeline

1. La aplicación persiste datos en PostgreSQL.
2. El pipeline `load_data_pipeline.py` extrae tablas desde PostgreSQL.
3. dlt carga los datos crudos en DuckDB (dataset raw).
4. dbt transforma esos datos y materializa modelos analíticos.
5. Evidence consume los modelos para dashboards y análisis.

En resumen: **PostgreSQL -> dlt (raw) -> dbt (transformado) -> Evidence (reportes)**.

## 3. Cómo correrlo (paso a paso)

## Requisitos

- Docker
- `uv`
- Bun
- Variables de entorno (`env_templates` copiados a `.env.*` en la raíz)

## A. Levantar backend y base de datos

Desde la raíz del repo:

```bash
docker compose up --build
```

## B. Ejecutar migraciones y cargar datos fake

```bash
docker compose --profile migrations --profile load_fake up --build migration load_fake
```

Si quieres reiniciar la base desde cero:

```bash
docker compose down -v
docker compose --profile migrations --profile load_fake up --build migration load_fake
```

## C. Ejecutar el pipeline ELT (dlt + dbt)

```bash
cd analytics/dlt_pipeline
uv sync
uv run load_data_pipeline.py
```

## D. Levantar reportes (Evidence)

```bash
cd analytics/dbt/reports
bun install
bun run sources
bun run dev
```

## 4. Qué se transforma actualmente

El flujo analítico actual está enfocado principalmente en usuarios/perfiles, con modelos orientados a:

- estado de usuarios,
- señales recientes de churn/nuevos usuarios,
- ranking y distribución de reputación.

## 5. Archivos clave

- `/home/runner/work/backend/backend/analytics/dlt_pipeline/load_data_pipeline.py`
- `/home/runner/work/backend/backend/analytics/dbt`
- `/home/runner/work/backend/backend/analytics/dbt/reports`
- `/home/runner/work/backend/backend/compose.yaml`
