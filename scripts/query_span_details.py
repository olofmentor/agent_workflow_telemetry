#!/usr/bin/env python3
"""Query OpenTelemetry spans from Databricks to see LLM interaction details"""

import os
from dotenv import load_dotenv
from databricks import sql

load_dotenv()

# Get Databricks connection info
server_hostname = "adb-957977613266276.16.azuredatabricks.net"
http_path = "/sql/1.0/warehouses/28cb43e5fe61c5a2"
access_token = os.getenv("DATABRICKS_TOKEN")

print("Connecting to Databricks...")
connection = sql.connect(
    server_hostname=server_hostname,
    http_path=http_path,
    access_token=access_token
)

cursor = connection.cursor()

# Query recent spans with attributes
query = """
SELECT 
    span_name,
    service_name,
    attributes,
    status_message,
    start_time_unix_nano,
    end_time_unix_nano
FROM dev_ai.agent_traces.mlflow_experiment_trace_otel_spans
WHERE service_name = 'SE_workflow_test'
ORDER BY start_time_unix_nano DESC
LIMIT 10
"""

print("\nRecent spans from SE_workflow_test:\n")
cursor.execute(query)

for row in cursor.fetchall():
    span_name, service_name, attributes, status_msg, start_time, end_time = row
    duration_ms = (end_time - start_time) / 1_000_000
    
    print(f"Span: {span_name}")
    print(f"  Service: {service_name}")
    print(f"  Duration: {duration_ms:.2f}ms")
    if status_msg:
        print(f"  Status: {status_msg}")
    if attributes:
        print(f"  Attributes: {attributes[:500]}...")  # First 500 chars
    print()

cursor.close()
connection.close()

print("✓ Query complete")
