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
    from azure.monitor.opentelemetry.exporter import (
        AzureMonitorTraceExporter,
    )
except Exception:  # pragma: no cover - optional dependency
    AzureMonitorTraceExporter = None


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


class AzureOtelSink(TelemetrySink):
    def __init__(self, connection_string: str, app_name: str) -> None:
        if not AzureMonitorTraceExporter:
            raise RuntimeError(
                "azure-monitor-opentelemetry-exporter is not installed."
            )
        resource = Resource.create({"service.name": app_name})
        provider = TracerProvider(resource=resource)
        exporter = AzureMonitorTraceExporter(
            connection_string=connection_string
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(app_name)

    def record(self, event: TelemetryEvent) -> None:
        with self.tracer.start_as_current_span(event.name) as span:
            for key, value in event.attributes.items():
                span.set_attribute(key, _coerce_str(value))


def create_sink(app_name: str) -> TelemetrySink:
    dest = os.environ.get("LOG_DEST", "local").lower().strip()
    if dest == "azure":
        connection_string = os.environ.get(
            "APPLICATIONINSIGHTS_CONNECTION_STRING", ""
        )
        if not connection_string:
            logging.warning(
                "APPLICATIONINSIGHTS_CONNECTION_STRING is not set."
            )
            return NullSink()
        return AzureOtelSink(connection_string=connection_string, app_name=app_name)

    log_dir = os.environ.get("LOG_DIR", "./logs")
    return LocalMarkdownSink(base_dir=log_dir)
