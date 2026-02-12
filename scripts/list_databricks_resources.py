#!/usr/bin/env python3
"""
List available Databricks Unity Catalog schemas and tables.
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
WORKSPACE_URL = os.getenv("DATABRICKS_HOST", "https://adb-957977613266276.16.azuredatabricks.net").rstrip("/")


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

    print("Available Catalogs:")
    print("=" * 80)
    catalogs_url = f"{WORKSPACE_URL}/api/2.1/unity-catalog/catalogs"
    response = requests.get(catalogs_url, headers=headers)
    if response.status_code == 200:
        catalogs = response.json().get("catalogs", [])
        for cat in catalogs:
            print(f"  - {cat['name']}")
    else:
        print(f"Error listing catalogs: {response.status_code}")
        print(response.text[:300])

    print()
    print(f"Schemas in {CATALOG} catalog:")
    print("=" * 80)
    schemas_url = f"{WORKSPACE_URL}/api/2.1/unity-catalog/schemas?catalog_name={CATALOG}"
    response = requests.get(schemas_url, headers=headers)
    if response.status_code == 200:
        schemas = response.json().get("schemas", [])
        if schemas:
            for schema in schemas:
                print(f"  - {schema['name']}")
                tables_url = f"{WORKSPACE_URL}/api/2.1/unity-catalog/tables?catalog_name={CATALOG}&schema_name={schema['name']}"
                tables_response = requests.get(tables_url, headers=headers)
                if tables_response.status_code == 200:
                    tables = tables_response.json().get("tables", [])
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


if __name__ == "__main__":
    main()
