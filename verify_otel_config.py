#!/usr/bin/env python3
"""
Verify traces are being written to Databricks
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Checking OpenTelemetry Configuration...")
print("=" * 80)

# Check environment variables
endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
service_name = os.getenv('OTEL_SERVICE_NAME', 'SE_workflow_test')

print(f"✓ Service Name: {service_name}")
print(f"✓ Endpoint: {endpoint}")

if not endpoint:
    print("\n❌ ERROR: OTEL_EXPORTER_OTLP_ENDPOINT not set!")
    print("   Please check your .env file")
    sys.exit(1)

# Parse headers
headers = {}
if headers_str:
    for part in headers_str.split(','):
        if '=' in part:
            key, value = part.split('=', 1)
            headers[key.strip()] = value.strip()
            # Mask sensitive values
            if 'Bearer' in value:
                print(f"✓ Header: {key.strip()} = Bearer ***")
            else:
                print(f"✓ Header: {key.strip()} = {value.strip()}")

# Extract table name
table_name = headers.get('X-Databricks-UC-Table-Name', 'NOT SET')
print(f"✓ UC Table: {table_name}")

print("\n" + "=" * 80)
print("Configuration Summary:")
print("=" * 80)

if table_name == 'NOT SET':
    print("⚠️  No Unity Catalog table specified in headers")
    print("   Traces will go to default MLflow tables")
else:
    print(f"✓ Traces will be written to: {table_name}")

print(f"✓ Configuration is valid")
print("\nTo verify traces are being written:")
print(f"1. Run the workflow: adk run .")
print(f"2. Check Databricks MLflow UI:")
print(f"   https://adb-957977613266276.16.azuredatabricks.net/ml/experiments/3078644569850998/traces")
print(f"3. Or query the table:")
if table_name != 'NOT SET':
    print(f"   SELECT * FROM {table_name} WHERE service_name = '{service_name}' ORDER BY start_time DESC LIMIT 10;")
else:
    print(f"   SELECT * FROM dev_ai.agent_traces.mlflow_experiment_trace_otel_spans")
    print(f"   WHERE service_name = '{service_name}' ORDER BY start_time DESC LIMIT 10;")
