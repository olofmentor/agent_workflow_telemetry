-- Reference: MLflow Unity Catalog OTEL logs table (managed Delta).
-- Captured via: DESCRIBE TABLE EXTENDED dev_ai.agent_traces.mlflow_experiment_trace_otel_logs
-- Tables are created by MLflow set_experiment_trace_location — do not rely on this DDL to provision.

CREATE TABLE IF NOT EXISTS catalog.schema.mlflow_experiment_trace_otel_logs (
  event_name STRING,
  trace_id STRING,
  span_id STRING,
  time_unix_nano BIGINT,
  observed_time_unix_nano BIGINT,
  severity_number STRING,
  severity_text STRING,
  body STRING,
  attributes MAP<STRING, STRING>,
  dropped_attributes_count INT,
  flags INT,
  resource STRUCT<
    attributes: MAP<STRING, STRING>,
    dropped_attributes_count: INT
  >,
  resource_schema_url STRING,
  instrumentation_scope STRUCT<
    name: STRING,
    version: STRING,
    attributes: MAP<STRING, STRING>,
    dropped_attributes_count: INT
  >,
  log_schema_url STRING
)
USING DELTA
COMMENT 'Reference column layout only; actual table owned by MLflow UC trace linking';
