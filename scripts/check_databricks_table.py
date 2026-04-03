#!/usr/bin/env python3
"""
Check Databricks Unity Catalog table and permissions.

Default table matches MLflow GenAI trace OTEL spans
(``mlflow_experiment_trace_otel_spans`` in ``DATABRICKS_CATALOG`` / ``DATABRICKS_SCHEMA``).

Legacy table ``agent_traces.otel_traces`` is not used by this project; override with env vars below.

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

# Config (align with init / MLflow UC trace storage)
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

    full_table = f"{CATALOG}.{SCHEMA}.{TABLE}"
    print(f"Checking if {full_table} exists...")
    print("=" * 80)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    table_url = f"{WORKSPACE_URL}/api/2.1/unity-catalog/tables/{full_table}"
    response = requests.get(table_url, headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    print()

    if response.status_code == 200:
        print("✅ Table exists!")
    elif response.status_code == 404:
        print("❌ Table does not exist. Run `python -m init` or MLflow set_experiment_trace_location() after Terraform creates the schema.")
    elif response.status_code == 403:
        print("⚠️  Permission denied. You may not have access to this catalog/schema.")
        print(f"   Please ask your Databricks admin to grant:")
        print(f"   - USE CATALOG on {CATALOG}")
        print(f"   - USE SCHEMA on {CATALOG}.{SCHEMA}")
        print(f"   - SELECT, MODIFY on {full_table}")


if __name__ == "__main__":
    main()
