#!/bin/bash
# Script to run workflow with OpenTelemetry auto-instrumentation
cd /mnt/c/Users/xgranbolo/AICode/Workflow_demo
export PATH=$HOME/.local/bin:$PATH

# Run with OpenTelemetry instrumentation
echo "What are the key lessons learned and challenges from the cloud migration project?" | \
  opentelemetry-instrument --traces_exporter otlp \
  /home/xgranbolo/.local/bin/adk run agent_workflow_telemetry
