-- DDL for OpenTelemetry Traces Table in Unity Catalog
-- This table stores distributed traces from the agent workflow
-- 
-- Usage:
-- 1. Run this in Databricks SQL Editor or Notebook
-- 2. Update .env file with the table name: dev_ai.agent_traces.workflow_otel_traces
-- 3. Grant permissions to your user/service principal

-- Create catalog if it doesn't exist (optional - may already exist)
-- CREATE CATALOG IF NOT EXISTS dev_ai;

-- Create schema for agent traces
CREATE SCHEMA IF NOT EXISTS dev_ai.agent_traces
COMMENT 'Schema for storing agent workflow telemetry and traces';

-- Create the traces table
CREATE TABLE IF NOT EXISTS dev_ai.agent_traces.workflow_otel_traces (
  -- Trace identification
  trace_id STRING NOT NULL COMMENT 'Unique identifier for the entire trace',
  span_id STRING NOT NULL COMMENT 'Unique identifier for this span',
  parent_span_id STRING COMMENT 'Parent span ID for nested spans',
  
  -- Span metadata
  name STRING NOT NULL COMMENT 'Name/operation of the span',
  kind STRING COMMENT 'Span kind: INTERNAL, SERVER, CLIENT, PRODUCER, CONSUMER',
  status_code STRING COMMENT 'Status code: OK, ERROR, UNSET',
  status_message STRING COMMENT 'Status message for errors',
  
  -- Timing information
  start_time TIMESTAMP NOT NULL COMMENT 'When the span started',
  end_time TIMESTAMP NOT NULL COMMENT 'When the span ended',
  duration_ms BIGINT COMMENT 'Duration in milliseconds',
  
  -- Service information
  service_name STRING COMMENT 'Name of the service (e.g., SE_workflow_test)',
  service_version STRING COMMENT 'Version of the service',
  
  -- Resource attributes (as JSON)
  resource_attributes STRING COMMENT 'Service resource attributes as JSON',
  
  -- Span attributes (as JSON)
  span_attributes STRING COMMENT 'Span-specific attributes as JSON',
  
  -- Events (as JSON array)
  events STRING COMMENT 'Span events as JSON array',
  
  -- Links to other traces (as JSON array)
  links STRING COMMENT 'Links to other traces as JSON array',
  
  -- Instrumentation
  instrumentation_library_name STRING COMMENT 'Name of the instrumentation library',
  instrumentation_library_version STRING COMMENT 'Version of the instrumentation library',
  
  -- MLflow integration
  mlflow_experiment_id STRING COMMENT 'MLflow experiment ID',
  mlflow_run_id STRING COMMENT 'MLflow run ID if applicable',
  
  -- Metadata
  ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP() COMMENT 'When the trace was ingested',
  
  -- Agent-specific fields (optional)
  agent_name STRING COMMENT 'Name of the agent (e.g., Clarifier, Synthesizer)',
  workflow_id STRING COMMENT 'Unique workflow execution ID',
  user_id STRING COMMENT 'User who triggered the workflow'
)
USING DELTA
PARTITIONED BY (DATE(start_time))
COMMENT 'OpenTelemetry traces from agent workflows'
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true',
  'delta.enableChangeDataFeed' = 'false'
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_trace_id 
ON dev_ai.agent_traces.workflow_otel_traces (trace_id);

CREATE INDEX IF NOT EXISTS idx_span_id 
ON dev_ai.agent_traces.workflow_otel_traces (span_id);

CREATE INDEX IF NOT EXISTS idx_service_time 
ON dev_ai.agent_traces.workflow_otel_traces (service_name, start_time);

-- Grant permissions to your user
-- Replace with your actual username or service principal
GRANT USE CATALOG ON CATALOG dev_ai TO `olof.granberg@partners.stockholmexergi.se`;
GRANT USE SCHEMA ON SCHEMA dev_ai.agent_traces TO `olof.granberg@partners.stockholmexergi.se`;
GRANT SELECT, MODIFY ON TABLE dev_ai.agent_traces.workflow_otel_traces TO `olof.granberg@partners.stockholmexergi.se`;

-- Verify the table was created
DESCRIBE TABLE EXTENDED dev_ai.agent_traces.workflow_otel_traces;

-- Sample query to verify structure
-- SELECT * FROM dev_ai.agent_traces.workflow_otel_traces LIMIT 10;
