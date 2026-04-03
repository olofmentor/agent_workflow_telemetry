"""Tests for observability/otlp_headers.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from observability.otlp_headers import format_otel_headers, merge_otel_header_string, parse_otel_headers


def test_parse_roundtrip():
    s = "Authorization=Bearer abc,x-mlflow-experiment-id=42"
    d = parse_otel_headers(s)
    assert d["Authorization"] == "Bearer abc"
    assert d["x-mlflow-experiment-id"] == "42"


def test_merge_preserves_and_updates():
    base = "Authorization=Bearer old,x-mlflow-experiment-id=1"
    merged = merge_otel_header_string(
        base,
        {"x-mlflow-experiment-id": "99", "X-Databricks-UC-Table-Name": "catalog.schema.t"},
    )
    d = parse_otel_headers(merged)
    assert d["Authorization"] == "Bearer old"
    assert d["x-mlflow-experiment-id"] == "99"
    assert d["X-Databricks-UC-Table-Name"] == "catalog.schema.t"


def test_format_otel_headers_authorization_first():
    d = {"z": "1", "Authorization": "Bearer x"}
    s = format_otel_headers(d)
    assert s.startswith("Authorization=")

