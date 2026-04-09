-- Reference: MLflow Unity Catalog OTEL spans table (managed Delta).
-- Captured via: DESCRIBE TABLE EXTENDED dev_ai.agent_traces.mlflow_experiment_trace_otel_spans
-- Tables are created by MLflow set_experiment_trace_location — do not rely on this DDL to provision.
-- Typical properties: Provider delta, otel.schemaVersion=v1, delta row-tracking internal columns.

-- Example logical schema (Spark / Unity Catalog types):
CREATE TABLE IF NOT EXISTS catalog.schema.mlflow_experiment_trace_otel_spans (
  trace_id STRING,
  span_id STRING,
  trace_state STRING,
  parent_span_id STRING,
  flags INT,
  name STRING,
  kind STRING,
  start_time_unix_nano BIGINT,
  end_time_unix_nano BIGINT,
  attributes MAP<STRING, STRING>,
  dropped_attributes_count INT,
  events ARRAY<
    STRUCT<
      time_unix_nano: BIGINT,
      name: STRING,
      attributes: MAP<STRING, STRING>,
      dropped_attributes_count: INT
    >
  >,
  dropped_events_count INT,
  links ARRAY<
    STRUCT<
      trace_id: STRING,
      span_id: STRING,
      trace_state: STRING,
      attributes: MAP<STRING, STRING>,
      dropped_attributes_count: INT,
      flags: INT
    >
  >,
  dropped_links_count INT,
  status STRUCT<
    message: STRING,
    code: STRING
  >,
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
  span_schema_url STRING
)
USING DELTA
COMMENT 'Reference column layout only; actual table owned by MLflow UC trace linking';
