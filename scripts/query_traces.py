#!/usr/bin/env python3
"""
Check access to the MLflow GenAI OTEL spans table in Unity Catalog.

Table resolution matches ``scripts/check_databricks_table.py``:
``DATABRICKS_CATALOG``, ``DATABRICKS_SCHEMA``, ``DATABRICKS_OTEL_SPANS_TABLE``.

Requires: pip install requests python-dotenv
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

import requests

CATALOG = os.getenv("DATABRICKS_CATALOG", "dev_ai")
SCHEMA = os.getenv("DATABRICKS_SCHEMA", "mlflow_traces")
TABLE = os.getenv(
    "DATABRICKS_OTEL_SPANS_TABLE",
    "mlflow_experiment_trace_otel_spans",
)
WORKSPACE_URL = os.getenv(
    "DATABRICKS_HOST", "https://adb-957977613266276.16.azuredatabricks.net"
).rstrip("/")


def main():
    token = None
    headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    for part in headers_str.split(","):
        if "Authorization=Bearer" in part:
            token = part.split("Bearer ")[1].strip()
            break

    if not token:
        print("❌ No token found in OTEL_EXPORTER_OTLP_HEADERS")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    full_table = f"{CATALOG}.{SCHEMA}.{TABLE}"

    print(f"Checking for traces table {full_table}...")
    print("=" * 80)

    table_url = f"{WORKSPACE_URL}/api/2.1/unity-catalog/tables/{full_table}"
    response = requests.get(table_url, headers=headers)

    print(f"Table access status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Table accessible")
        table_info = response.json()
        print(f"   Table type: {table_info.get('table_type')}")
        print(f"   Data source: {table_info.get('data_source_format')}")
    else:
        print(f"❌ Cannot access table: {response.text[:200]}")

    print()
    print("=" * 80)
    print("To query traces, use Databricks SQL or Notebook:")
    print(f"   SELECT * FROM {full_table}")
    print("   ORDER BY start_time DESC LIMIT 10;")
    print()
    print("Or check the MLflow UI in your Databricks workspace.")


if __name__ == "__main__":
    main()
