# Explicación del Data Pipeline e Infraestructura (Marketplace Andes)

## 1) ¿Cómo funciona el data pipeline?

El flujo actual es un **ELT** (Extract, Load, Transform) con estos pasos:

1. **Fuente transaccional (PostgreSQL)**
   - La aplicación backend guarda usuarios y perfiles en PostgreSQL (`users`, `user_profiles`, etc.).
   - Las migraciones crean y evolucionan el esquema (Alembic).
   - Para ambientes de desarrollo/demo, `load_fake` genera datos sintéticos (incluyendo usuarios con historial de fechas y ratings).

2. **Extracción y carga con dlt**
   - El script `analytics/dlt_pipeline/load_data_pipeline.py` usa `dlt` + `sql_database`.
   - Extrae recursos de la BD transaccional: `users` y `user_profiles`.
   - Carga en DuckDB (`analytics.duckdb`) dentro del dataset raw `marketplace_andes_analytics_raw`.
   - La tabla `users` se carga de forma incremental usando `updated_at`.

3. **Transformación con dbt**
   - En el mismo script, después del load, se ejecuta `dbt.run_all()` sobre el proyecto `analytics/dbt`.
   - dbt toma como fuente el dataset raw (`dlt_raw`) y materializa modelos en `marketplace_andes_analytics`.
   - Modelos actuales:
     - `fact_user_stats`: estado actual del usuario, flags de “nuevo en 30 días” y “churn reciente”.
     - `best_reputation`: ranking de usuarios activos con rating válido (1 a 5), incluyendo representación en estrellas.

4. **Consumo analítico / visualización**
   - **Evidence** (en `analytics/dbt/reports`) se conecta al mismo `analytics.duckdb`.
   - Las páginas consultan modelos dbt y exponen visualizaciones/tablas para análisis de negocio.

---

## 2) ¿Cómo es la infraestructura?

### Infraestructura operacional (app)
- **Orquestación**: `docker compose`.
- **Servicios base**:
  - `server` (FastAPI backend),
  - `postgres` (BD transaccional),
  - opcionales por perfiles: `migration`, `load_fake`, `pgadmin`, `otel_collector`.
- Flujo típico en local:
  1. levantar Postgres + server,
  2. correr migraciones (perfil `migrations`),
  3. cargar datos fake (perfil `load_fake`).

### Infraestructura analítica
- **Motor analítico local**: DuckDB (archivo `analytics.duckdb` en `analytics/dbt/reports/sources/marketplace_andes/`).
- **Orquestación ELT**: script Python con `dlt` + `dbt` (`uv run load_data_pipeline.py`).
- **Capa de reporting**: Evidence (`bun run sources` + `bun run dev`).
- En resumen:
  - **OLTP**: PostgreSQL (backend),
  - **Analítica**: DuckDB (dataset raw + modelos transformados),
  - **BI**: Evidence.

---

## 3) ¿Qué business questions se han respondido hasta ahora?

Con los modelos y reportes actuales, ya se responden principalmente estas preguntas:

1. **¿Cómo está distribuida la base de usuarios por estado actual?**
   - Activos vs churned (distribución de estado).

2. **¿Cuál es la volatilidad reciente de usuarios?**
   - Cuántos usuarios son nuevos en los últimos 30 días.
   - Cuántos usuarios hicieron churn recientemente (últimos 30 días).

3. **¿Quiénes son los estudiantes con mejor reputación?**
   - Top/ranking por rating entre usuarios activos y con rating válido.

4. **¿Cómo se distribuyen los ratings de reputación?**
   - Número de usuarios por calificación (1–5 estrellas).

---

## 4) Alcance actual y notas

- El pipeline analítico actual está centrado en el dominio de **usuarios/perfiles**.
- El enfoque de negocio vigente está en **retención/churn** y **reputación**.
- No se observan aún métricas analíticas de otras áreas del marketplace (por ejemplo, listings, categorías, conversiones o revenue) dentro de este pipeline/reporting.
