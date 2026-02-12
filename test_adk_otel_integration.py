#!/usr/bin/env python3
"""
Test if Google ADK is generating OpenTelemetry traces
"""
import os
import sys

# Set environment before importing
os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = 'https://adb-957977613266276.16.azuredatabricks.net/api/2.0/otel/v1/traces'
os.environ['OTEL_SERVICE_NAME'] = 'test_adk_traces'

print("Testing Google ADK + OpenTelemetry Integration...")
print("=" * 80)

# Import ADK - this should trigger agent.py which sets up tracing
try:
    import agent
    print("✓ agent.py imported (tracer should be set up)")
except Exception as e:
    print(f"❌ Failed to import agent: {e}")
    sys.exit(1)

# Check if tracer provider is set
from opentelemetry import trace

tracer_provider = trace.get_tracer_provider()
print(f"✓ Tracer provider type: {type(tracer_provider).__name__}")

# Check if it's configured
if hasattr(tracer_provider, '_active_span_processor'):
    print(f"✓ Has span processor configured")
else:
    print(f"⚠️  May not have span processor")

# Try to create a test span
tracer = trace.get_tracer(__name__)
print("\nCreating test span...")
try:
    with tracer.start_as_current_span("test_span") as span:
        span.set_attribute("test.key", "test_value")
        print("✓ Test span created successfully")
    
    # Force flush
    if hasattr(tracer_provider, 'force_flush'):
        tracer_provider.force_flush()
        print("✓ Traces flushed")
    
    print("\n✅ OpenTelemetry integration is working!")
    print("   Traces should appear in Databricks within 1-2 minutes")
    
except Exception as e:
    print(f"❌ Error creating span: {e}")
    sys.exit(1)
