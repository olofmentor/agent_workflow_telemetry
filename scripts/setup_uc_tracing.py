#!/usr/bin/env python3
"""
Link an MLflow experiment to Unity Catalog trace storage (creates OTEL tables if needed).

Delegates to the ``init`` package. Prefer ``python -m init`` from the repo root.

See: https://learn.microsoft.com/en-us/azure/databricks/mlflow3/genai/tracing/trace-unity-catalog
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

from init import init_and_connect


def main() -> int:
    try:
        init_and_connect()
        return 0
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
