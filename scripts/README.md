# Databricks Utility Scripts

Helper scripts for Databricks Unity Catalog and trace validation.

**Requirements:** `pip install requests python-dotenv`

| Script | Purpose |
|--------|---------|
| `setup_uc_tracing.py` | One-time: link experiment to UC schema (enables metadata/spans/logs in UC tables) |
| `check_databricks_table.py` | Verify Unity Catalog table exists (for UC-backed trace storage) |
| `list_databricks_resources.py` | List catalogs, schemas, and tables |
| `query_traces.py` | Check access to MLflow traces table |

**Environment:** Uses `OTEL_EXPORTER_OTLP_HEADERS` for the Databricks token. For `setup_uc_tracing.py`: `MLFLOW_TRACING_SQL_WAREHOUSE_ID` (required), `DATABRICKS_CATALOG` (default: main), `DATABRICKS_SCHEMA` (default: mlflow_traces), `MLFLOW_EXPERIMENT_ID` or `MLFLOW_EXPERIMENT_NAME`.
