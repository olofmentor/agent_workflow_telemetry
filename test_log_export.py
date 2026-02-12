#!/usr/bin/env python3
"""Test script to verify OpenTelemetry log export to Databricks"""

import os
import logging
import time
from dotenv import load_dotenv

load_dotenv()

from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource

# Get OTEL configuration
endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
headers_str = os.getenv('OTEL_EXPORTER_OTLP_HEADERS', '')
service_name = os.getenv('OTEL_SERVICE_NAME', 'log_test_service')

print(f"Configuring log exporter...")
print(f"  Service: {service_name}")

# Parse headers
headers = {}
if headers_str:
    for part in headers_str.split(','):
        if '=' in part:
            key, value = part.split('=', 1)
            headers[key.strip()] = value.strip()

# Setup logs endpoint
logs_endpoint = endpoint.replace('/traces', '/logs')
print(f"  Endpoint: {logs_endpoint}")

# Create resource and logger provider
resource = Resource.create({"service.name": service_name})
log_exporter = OTLPLogExporter(endpoint=logs_endpoint, headers=headers)
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

# Attach handler to root logger
handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)

print(f"✓ Logger configured")

# Create test logger and emit logs
logger = logging.getLogger(__name__)

print("\nEmitting test logs...")
logger.info("Test log entry 1: INFO level")
logger.warning("Test log entry 2: WARNING level")
logger.error("Test log entry 3: ERROR level")
logger.info("Test log entry 4: INFO with metadata", extra={"test_id": "12345", "test_type": "log_export"})

print("  ✓ 4 log entries created")

# Force flush
print("\nFlushing logs...")
result = logger_provider.force_flush(timeout_millis=5000)
print(f"  Flush result: {result}")

# Shutdown
print("\nShutting down logger provider...")
logger_provider.shutdown()
print(f"  ✓ Shutdown complete")

print("\n✅ Test complete. Check Databricks for logs with service_name='log_test_service'")
