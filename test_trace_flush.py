#!/usr/bin/env python3
"""
Check if traces are reaching Databricks and force a flush
"""
import os
import time
from dotenv import load_dotenv

load_dotenv()

print("Testing trace export with force flush...")
print("=" * 80)

# Setup OpenTelemetry exactly as agent.py does
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource

endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
service_name = os.getenv('OTEL_SERVICE_NAME', 'trace_flush_test')

headers = {}
if headers_str:
    for part in headers_str.split(','):
        if '=' in part:
            key, value = part.split('=', 1)
            headers[key.strip()] = value.strip()

resource = Resource.create({"service.name": service_name})
tracer_provider = TracerProvider(resource=resource)
exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
processor = BatchSpanProcessor(exporter)
tracer_provider.add_span_processor(processor)
trace.set_tracer_provider(tracer_provider)

print(f"✓ Tracer configured: {service_name}")

# Create multiple test spans
tracer = trace.get_tracer(__name__)

print("Creating test spans...")
for i in range(3):
    with tracer.start_as_current_span(f"test_span_{i}") as span:
        span.set_attribute("test.iteration", i)
        span.set_attribute("test.timestamp", str(time.time()))
        time.sleep(0.1)
    print(f"  ✓ Span {i} created")

# Force flush
print("\nForcing flush...")
result = tracer_provider.force_flush(timeout_millis=5000)
print(f"  Flush result: {result}")

# Shutdown to ensure all spans are exported
print("\nShutting down tracer provider...")
tracer_provider.shutdown()
print("  ✓ Shutdown complete")

print("\n" + "=" * 80)
print("✅ Test complete!")
print("\nCheck Databricks for traces with service_name='trace_flush_test':")
print("SELECT * FROM dev_ai.agent_traces.mlflow_experiment_trace_otel_spans")
print("WHERE service_name = 'trace_flush_test'")
print("ORDER BY start_time_unix_nano DESC;")
