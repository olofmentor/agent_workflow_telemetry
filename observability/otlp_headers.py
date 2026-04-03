"""Parse and merge Databricks OTLP exporter headers (comma-separated key=value)."""

from __future__ import annotations


def parse_otel_headers(headers_str: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in headers_str.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        key, value = part.split("=", 1)
        out[key.strip()] = value.strip()
    return out


def format_otel_headers(headers: dict[str, str]) -> str:
    """Serialize headers; Authorization first when present for stable diffs."""
    keys = sorted(headers.keys(), key=lambda k: (0 if k.lower() == "authorization" else 1, k))
    return ",".join(f"{k}={headers[k]}" for k in keys)


def merge_otel_header_string(existing: str, updates: dict[str, str]) -> str:
    base = parse_otel_headers(existing) if existing.strip() else {}
    base.update(updates)
    return format_otel_headers(base)
