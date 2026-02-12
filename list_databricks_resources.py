#!/usr/bin/env python3
"""
List available schemas and tables
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Get token
token = None
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
for part in headers_str.split(','):
    if 'Authorization=Bearer' in part:
        token = part.split('Bearer ')[1].strip()
        break

if not token:
    print("❌ No token found")
    exit(1)

workspace_url = "https://adb-957977613266276.16.azuredatabricks.net"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# List catalogs
print("Available Catalogs:")
print("=" * 80)
catalogs_url = f"{workspace_url}/api/2.1/unity-catalog/catalogs"
response = requests.get(catalogs_url, headers=headers)
if response.status_code == 200:
    catalogs = response.json().get('catalogs', [])
    for cat in catalogs:
        print(f"  - {cat['name']}")
else:
    print(f"Error listing catalogs: {response.status_code}")
    print(response.text[:300])

print()

# Try to list schemas in dev_ai
print("Schemas in dev_ai catalog:")
print("=" * 80)
schemas_url = f"{workspace_url}/api/2.1/unity-catalog/schemas?catalog_name=dev_ai"
response = requests.get(schemas_url, headers=headers)
if response.status_code == 200:
    schemas = response.json().get('schemas', [])
    if schemas:
        for schema in schemas:
            print(f"  - {schema['name']}")
            
            # List tables in this schema
            tables_url = f"{workspace_url}/api/2.1/unity-catalog/tables?catalog_name=dev_ai&schema_name={schema['name']}"
            tables_response = requests.get(tables_url, headers=headers)
            if tables_response.status_code == 200:
                tables = tables_response.json().get('tables', [])
                if tables:
                    for table in tables:
                        print(f"      └─ {table['name']}")
                else:
                    print(f"      └─ (no tables)")
    else:
        print("  (no schemas found)")
else:
    print(f"Error listing schemas: {response.status_code}")
    print(response.text[:300])
