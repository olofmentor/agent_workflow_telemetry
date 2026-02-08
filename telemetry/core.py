import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
        OTLPSpanExporter,
    )
except Exception:  # pragma: no cover - optional dependency
    OTLPSpanExporter = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _coerce_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=True, default=str)
    except Exception:
        return str(value)


@dataclass
class TelemetryEvent:
    name: str
    attributes: dict[str, Any]
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = _utc_now()


class TelemetrySink:
    def record(self, event: TelemetryEvent) -> None:
        raise NotImplementedError


class NullSink(TelemetrySink):
    def record(self, event: TelemetryEvent) -> None:
        return None


class LocalMarkdownSink(TelemetrySink):
    def __init__(self, base_dir: str) -> None:
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def record(self, event: TelemetryEvent) -> None:
        session_id = event.attributes.get("session_id", "unknown")
        path = os.path.join(self.base_dir, f"session_{session_id}.md")
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(f"## {event.name}\n")
            handle.write(f"- timestamp: {event.timestamp}\n")
            for key, value in event.attributes.items():
                handle.write(f"- {key}: {_coerce_str(value)}\n")
            handle.write("\n")


class DatabricksOtelSink(TelemetrySink):
    def __init__(
        self,
        endpoint: str,
        token: str,
        app_name: str,
        experiment_id: str | None = None,
    ) -> None:
        if not OTLPSpanExporter:
            raise RuntimeError(
                "opentelemetry-exporter-otlp is not installed."
            )
        headers = {"Authorization": f"Bearer {token}"}
        if experiment_id:
            headers["x-mlflow-experiment-id"] = experiment_id
        resource = Resource.create({"service.name": app_name})
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(app_name)

    def record(self, event: TelemetryEvent) -> None:
        with self.tracer.start_as_current_span(event.name) as span:
            for key, value in event.attributes.items():
                span.set_attribute(key, _coerce_str(value))


def create_sink(app_name: str) -> TelemetrySink:
    dest = os.environ.get("LOG_DEST", "local").lower().strip()
    if dest == "databricks":
        endpoint = os.environ.get("DATABRICKS_OTLP_ENDPOINT", "").strip()
        host = os.environ.get("DATABRICKS_HOST", "").strip()
        if not endpoint and host:
            endpoint = host.rstrip("/") + "/api/2.0/otel/v1/traces"
        if not endpoint:
            logging.warning(
                "DATABRICKS_OTLP_ENDPOINT or DATABRICKS_HOST is not set."
            )
            return NullSink()
        token = os.environ.get("DATABRICKS_TOKEN", "").strip()
        if not token:
            logging.warning("DATABRICKS_TOKEN is not set.")
            return NullSink()
        experiment_id = os.environ.get(
            "DATABRICKS_MLFLOW_EXPERIMENT_ID", ""
        ).strip()
        return DatabricksOtelSink(
            endpoint=endpoint,
            token=token,
            app_name=app_name,
            experiment_id=experiment_id or None,
        )

    log_dir = os.environ.get("LOG_DIR", "./logs")
    return LocalMarkdownSink(base_dir=log_dir)
