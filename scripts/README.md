# Databricks Utility Scripts

Helper scripts for Databricks Unity Catalog and trace validation.

**Requirements:** `pip install requests python-dotenv`

| Script | Purpose |
|--------|---------|
| `check_databricks_table.py` | Verify Unity Catalog table exists (for UC-backed trace storage) |
| `list_databricks_resources.py` | List catalogs, schemas, and tables |
| `query_traces.py` | Check access to MLflow traces table |

**Environment:** Uses `OTEL_EXPORTER_OTLP_HEADERS` for the Databricks token. Optional: `DATABRICKS_CATALOG` (default: `dev_ai`), `DATABRICKS_HOST`.
