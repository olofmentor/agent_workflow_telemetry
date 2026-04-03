# Databricks Utility Scripts

Helper scripts for Databricks Unity Catalog and trace validation.

**Note:** Smoke scripts in the **repo root** (`test_trace_flush.py`, `test_log_export.py`, `test_adk_otel_integration.py`, `verify_otel_config.py`) are **not** run by `pytest` (see `pyproject.toml` `testpaths`). Run them manually against a configured workspace.

**`verify_otel_config.py` vs `python -m init --dry-run`:** Use **`verify_otel_config.py`** when you already have a `.env` and want a quick sanity check of OTLP variables (and optional connectivity) before running the app. Use **`python -m init --dry-run`** when you want to see what **`init`** would compute (MLflow experiment linking, merged headers, endpoint derivation) **without** applying changes—e.g. after editing catalog/schema or when bootstrapping UC tables for the first time.

**Requirements:** `pip install requests python-dotenv`

| Entry | Purpose |
|--------|---------|
| `python -m init` (repo root) | Preferred: load `.env`, create UC OTEL tables if needed, create/resolve experiment, set `OTEL_EXPORTER_OTLP_*` |
| `setup_uc_tracing.py` | Same as `python -m init` (wrapper for legacy docs) |
| `check_databricks_table.py` | Verify Unity Catalog table exists (for UC-backed trace storage) |
| `list_databricks_resources.py` | List catalogs, schemas, and tables |
| `query_traces.py` | Check access to MLflow traces table |

**Environment:** Uses `OTEL_EXPORTER_OTLP_HEADERS` for the Databricks token. For `setup_uc_tracing.py`: `MLFLOW_TRACING_SQL_WAREHOUSE_ID` (required), `DATABRICKS_CATALOG` (default: main), `DATABRICKS_SCHEMA` (default: mlflow_traces), `MLFLOW_EXPERIMENT_ID` or `MLFLOW_EXPERIMENT_NAME`.
