#!/usr/bin/env python3
"""
Check Databricks table and permissions
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get token from environment
token = None
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
for part in headers_str.split(','):
    if 'Authorization=Bearer' in part:
        token = part.split('Bearer ')[1].strip()
        break

if not token:
    print("❌ No token found in OTEL_EXPORTER_OTLP_HEADERS")
    exit(1)

workspace_url = "https://adb-957977613266276.16.azuredatabricks.net"

# Check if table exists
print("Checking if dev_ai.agent_traces.otel_traces exists...")
print("=" * 80)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Try to get table metadata
table_url = f"{workspace_url}/api/2.1/unity-catalog/tables/dev_ai.agent_traces.otel_traces"
response = requests.get(table_url, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")
print()

if response.status_code == 200:
    print("✅ Table exists!")
    
    # Try to query the table
    print("\nAttempting to query table for recent traces...")
    query_url = f"{workspace_url}/api/2.0/sql/statements"
    query_data = {
        "statement": "SELECT COUNT(*) as trace_count FROM dev_ai.agent_traces.otel_traces",
        "warehouse_id": "auto"  # Will need actual warehouse ID
    }
    
    query_response = requests.post(query_url, headers=headers, json=query_data)
    print(f"Query Status: {query_response.status_code}")
    print(f"Query Response: {query_response.text[:500]}")
    
elif response.status_code == 404:
    print("❌ Table does not exist. Please run the DDL script:")
    print("   create_otel_traces_simple.sql")
    
elif response.status_code == 403:
    print("⚠️  Permission denied. You may not have access to this catalog/schema.")
    print("   Please ask your Databricks admin to grant:")
    print("   - USE CATALOG on dev_ai")
    print("   - USE SCHEMA on dev_ai.agent_traces")
    print("   - SELECT, MODIFY on dev_ai.agent_traces.otel_traces")
