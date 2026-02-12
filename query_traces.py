#!/usr/bin/env python3
"""
Query traces from Databricks
"""
import os
import requests
from dotenv import load_dotenv
import time

load_dotenv()

# Get token
token = None
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
for part in headers_str.split(','):
    if 'Authorization=Bearer' in part:
        token = part.split('Bearer ')[1].strip()
        break

workspace_url = "https://adb-957977613266276.16.azuredatabricks.net"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("Checking for traces in dev_ai.agent_traces.mlflow_experiment_trace_otel_spans...")
print("=" * 80)

# Check if we can access the table
table_url = f"{workspace_url}/api/2.1/unity-catalog/tables/dev_ai.agent_traces.mlflow_experiment_trace_otel_spans"
response = requests.get(table_url, headers=headers)

print(f"Table access status: {response.status_code}")
if response.status_code == 200:
    print("✅ Table accessible")
    table_info = response.json()
    print(f"   Table type: {table_info.get('table_type')}")
    print(f"   Data source: {table_info.get('data_source_format')}")
else:
    print(f"❌ Cannot access table: {response.text[:200]}")

print("\n" + "=" * 80)
print("Note: To query the table data, you need to:")
print("1. Go to Databricks SQL or Notebook")
print("2. Run:")
print("   SELECT * FROM dev_ai.agent_traces.mlflow_experiment_trace_otel_spans")
print("   ORDER BY start_time DESC LIMIT 10;")
print("\nOr check the MLflow UI:")
print("https://adb-957977613266276.16.azuredatabricks.net/ml/experiments/3078644569850998/traces")
