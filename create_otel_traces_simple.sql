-- Simplified DDL for Databricks-compatible OTEL Traces Table
-- This matches the standard schema expected by Databricks OTEL endpoint
--
-- Run this in Databricks SQL Editor or Notebook, then update your .env file

-- Create schema
CREATE SCHEMA IF NOT EXISTS dev_ai.agent_traces
COMMENT 'Schema for agent workflow telemetry';

-- Create traces table matching Databricks OTEL format
CREATE TABLE IF NOT EXISTS dev_ai.agent_traces.otel_traces (
  trace_id STRING NOT NULL,
  span_id STRING NOT NULL,
  parent_span_id STRING,
  name STRING NOT NULL,
  kind STRING,
  start_time TIMESTAMP NOT NULL,
  end_time TIMESTAMP NOT NULL,
  attributes MAP<STRING, STRING>,
  events ARRAY<STRUCT<
    timestamp: TIMESTAMP,
    name: STRING,
    attributes: MAP<STRING, STRING>
  >>,
  status_code STRING,
  status_message STRING,
  resource_attributes MAP<STRING, STRING>,
  scope_name STRING,
  scope_version STRING,
  _ingestion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
)
USING DELTA
PARTITIONED BY (DATE(start_time))
COMMENT 'OpenTelemetry traces from agent workflows';

-- Grant permissions
GRANT USE CATALOG ON CATALOG dev_ai TO `olof.granberg@partners.stockholmexergi.se`;
GRANT USE SCHEMA ON SCHEMA dev_ai.agent_traces TO `olof.granberg@partners.stockholmexergi.se`;
GRANT SELECT, MODIFY ON TABLE dev_ai.agent_traces.otel_traces TO `olof.granberg@partners.stockholmexergi.se`;

-- Verify
DESCRIBE TABLE EXTENDED dev_ai.agent_traces.otel_traces;
