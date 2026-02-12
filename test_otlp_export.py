#!/usr/bin/env python3
"""
Simple test to verify OTLP export to Databricks is working.
"""
import os
import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Load environment
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

def test_trace_export():
    """Test that we can export a trace to Databricks."""
    print("Testing OTLP trace export to Databricks...")
    print("=" * 80)
    
    # Get config from environment
    endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
    headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
    service_name = os.getenv('OTEL_SERVICE_NAME', 'test_service')
    
    print(f"Endpoint: {endpoint}")
    print(f"Service Name: {service_name}")
    print(f"Headers configured: {bool(headers_str)}")
    print()
    
    # Parse headers
    headers = {}
    if headers_str:
        for part in headers_str.split(','):
            if '=' in part:
                key, value = part.split('=', 1)
                headers[key.strip()] = value.strip()
    
    # Create tracer
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=endpoint, headers=headers)
    processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    tracer = trace.get_tracer(__name__)
    
    print("Sending test trace...")
    with tracer.start_as_current_span("test_trace_to_databricks") as span:
        span.set_attribute("test.type", "connectivity_check")
        span.set_attribute("test.timestamp", str(time.time()))
        with tracer.start_as_current_span("test_child_span") as child:
            child.set_attribute("child.operation", "verification")
            time.sleep(0.1)  # Simulate work
    
    # Force flush
    provider.force_flush()
    print("✓ Trace sent and flushed")
    print()
    print("Check Databricks in 1-2 minutes:")
    print("https://adb-957977613266276.16.azuredatabricks.net/ml/experiments/3078644569850998/traces")
    print()
    print("Look for a trace named 'test_trace_to_databricks'")

if __name__ == "__main__":
    test_trace_export()
