#!/usr/bin/env python3
"""
Check access to MLflow traces table in Databricks.
For MLflow experiment traces, Databricks may store in a table like
{ catalog }.agent_traces.mlflow_experiment_trace_otel_spans.
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
TABLE = "mlflow_experiment_trace_otel_spans"
WORKSPACE_URL = os.getenv("DATABRICKS_HOST", "https://adb-957977613266276.16.azuredatabricks.net").rstrip("/")


def main():
    token = None
    headers_str = os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")
    for part in headers_str.split(","):
        if "Authorization=Bearer" in part:
            token = part.split("Bearer ")[1].strip()
            break

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    full_table = f"{CATALOG}.agent_traces.{TABLE}"

    print(f"Checking for traces in {full_table}...")
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
