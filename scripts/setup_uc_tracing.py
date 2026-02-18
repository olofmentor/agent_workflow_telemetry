#!/usr/bin/env python3
"""
One-time setup to link an MLflow experiment to a Unity Catalog schema.
This enables trace ingestion into UC tables (spans, logs, metadata).

Run once per experiment before sending traces via OTLP.
See: https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/trace-unity-catalog
"""
import os
import sys
from pathlib import Path

# Load .env from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


def parse_experiment_id_from_headers() -> str | None:
    """Extract x-mlflow-experiment-id from OTEL_EXPORTER_OTLP_HEADERS."""
    headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    for part in headers_str.split(","):
        if "x-mlflow-experiment-id" in part.lower() and "=" in part:
            return part.split("=", 1)[1].strip()
    return None


def main() -> int:
    warehouse_id = os.getenv("MLFLOW_TRACING_SQL_WAREHOUSE_ID")
    catalog = os.getenv("DATABRICKS_CATALOG", "main")
    schema = os.getenv("DATABRICKS_SCHEMA", "mlflow_traces")
    experiment_id = os.getenv("MLFLOW_EXPERIMENT_ID") or parse_experiment_id_from_headers()
    experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME", "/Shared/agent_traces")

    if not warehouse_id:
        print("ERROR: MLFLOW_TRACING_SQL_WAREHOUSE_ID is required.")
        print("Set it in .env (find warehouse ID in your Databricks SQL warehouse URL).")
        return 1

    try:
        import mlflow
        from mlflow.entities import UCSchemaLocation
        from mlflow.tracing.enablement import set_experiment_trace_location
    except ImportError as e:
        print(f"ERROR: {e}")
        print("Install: pip install 'mlflow[databricks]>=3.9.0'")
        return 1

    mlflow.set_tracking_uri("databricks")
    os.environ["MLFLOW_TRACING_SQL_WAREHOUSE_ID"] = warehouse_id

    if experiment_id:
        print(f"Using experiment ID: {experiment_id}")
    else:
        print(f"Creating or getting experiment: {experiment_name}")
        exp = mlflow.get_experiment_by_name(experiment_name)
        if exp:
            experiment_id = exp.experiment_id
            print(f"Found experiment ID: {experiment_id}")
        else:
            experiment_id = mlflow.create_experiment(name=experiment_name)
            print(f"Created experiment ID: {experiment_id}")

    print(f"Linking experiment to UC: {catalog}.{schema}")
    result = set_experiment_trace_location(
        location=UCSchemaLocation(catalog_name=catalog, schema_name=schema),
        experiment_id=experiment_id,
    )
    print(f"OK: Tables created at {result.full_otel_spans_table_name}")
    print("Metadata and other UC tables will now be populated when traces are sent.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
