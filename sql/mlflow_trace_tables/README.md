# MLflow experiment trace objects (Unity Catalog reference)

These `.sql` files document the **column layout** of the OTEL trace tables and the **definition text** of the companion views, as captured from `DESCRIBE TABLE EXTENDED` in a Databricks workspace.

**Do not use the table DDL to provision storage.** Tables are **managed Delta** objects created by MLflow when you call `set_experiment_trace_location` (see `uv run python -m init`). The DDL here is for documentation, codegen, and diffs when your workspace or MLflow version changes.

| File | Object | Type |
|------|--------|------|
| [`mlflow_experiment_trace_otel_spans.sql`](mlflow_experiment_trace_otel_spans.sql) | `mlflow_experiment_trace_otel_spans` | Managed table |
| [`mlflow_experiment_trace_otel_logs.sql`](mlflow_experiment_trace_otel_logs.sql) | `mlflow_experiment_trace_otel_logs` | Managed table |
| [`mlflow_experiment_trace_otel_metrics.sql`](mlflow_experiment_trace_otel_metrics.sql) | `mlflow_experiment_trace_otel_metrics` | Managed table |
| [`mlflow_experiment_trace_metadata.sql`](mlflow_experiment_trace_metadata.sql) | `mlflow_experiment_trace_metadata` | View |
| [`mlflow_experiment_trace_unified.sql`](mlflow_experiment_trace_unified.sql) | `mlflow_experiment_trace_unified` | View |

**Catalog and schema:** examples use `` `dev_ai`.`agent_traces` ``. Replace with your `DATABRICKS_CATALOG` and `DATABRICKS_SCHEMA` (or edit the view files before re-creating views in another environment).

Table properties typically include `otel.schemaVersion=v1` and Delta row-tracking columns (not listed as logical columns in these reference files).

## Example queries

See [`queries/README.md`](queries/README.md): per-agent session and token metrics, and span-by-span inputs/outputs for a trace.
