-- Reference: MLflow Unity Catalog OTEL metrics table (managed Delta).
-- Captured via: DESCRIBE TABLE EXTENDED dev_ai.agent_traces.mlflow_experiment_trace_otel_metrics
-- Tables are created by MLflow set_experiment_trace_location — do not rely on this DDL to provision.

CREATE TABLE IF NOT EXISTS catalog.schema.mlflow_experiment_trace_otel_metrics (
  name STRING,
  description STRING,
  unit STRING,
  metric_type STRING,
  gauge STRUCT<
    start_time_unix_nano: BIGINT,
    time_unix_nano: BIGINT,
    value: DOUBLE,
    exemplars: ARRAY<
      STRUCT<
        time_unix_nano: BIGINT,
        value: DOUBLE,
        span_id: STRING,
        trace_id: STRING,
        filtered_attributes: MAP<STRING, STRING>
      >
    >,
    attributes: MAP<STRING, STRING>,
    flags: INT
  >,
  sum STRUCT<
    start_time_unix_nano: BIGINT,
    time_unix_nano: BIGINT,
    value: DOUBLE,
    exemplars: ARRAY<
      STRUCT<
        time_unix_nano: BIGINT,
        value: DOUBLE,
        span_id: STRING,
        trace_id: STRING,
        filtered_attributes: MAP<STRING, STRING>
      >
    >,
    attributes: MAP<STRING, STRING>,
    flags: INT,
    aggregation_temporality: STRING,
    is_monotonic: BOOLEAN
  >,
  histogram STRUCT<
    start_time_unix_nano: BIGINT,
    time_unix_nano: BIGINT,
    count: BIGINT,
    sum: DOUBLE,
    bucket_counts: ARRAY<BIGINT>,
    explicit_bounds: ARRAY<DOUBLE>,
    exemplars: ARRAY<
      STRUCT<
        time_unix_nano: BIGINT,
        value: DOUBLE,
        span_id: STRING,
        trace_id: STRING,
        filtered_attributes: MAP<STRING, STRING>
      >
    >,
    attributes: MAP<STRING, STRING>,
    flags: INT,
    min: DOUBLE,
    max: DOUBLE,
    aggregation_temporality: STRING
  >,
  exponential_histogram STRUCT<
    attributes: MAP<STRING, STRING>,
    start_time_unix_nano: BIGINT,
    time_unix_nano: BIGINT,
    count: BIGINT,
    sum: DOUBLE,
    scale: INT,
    zero_count: BIGINT,
    positive_bucket: STRUCT<
      offset: INT,
      bucket_counts: ARRAY<BIGINT>
    >,
    negative_bucket: STRUCT<
      offset: INT,
      bucket_counts: ARRAY<BIGINT>
    >,
    flags: INT,
    exemplars: ARRAY<
      STRUCT<
        time_unix_nano: BIGINT,
        value: DOUBLE,
        span_id: STRING,
        trace_id: STRING,
        filtered_attributes: MAP<STRING, STRING>
      >
    >,
    min: DOUBLE,
    max: DOUBLE,
    zero_threshold: DOUBLE,
    aggregation_temporality: STRING
  >,
  summary STRUCT<
    start_time_unix_nano: BIGINT,
    time_unix_nano: BIGINT,
    count: BIGINT,
    sum: DOUBLE,
    quantile_values: ARRAY<
      STRUCT<
        quantile: DOUBLE,
        value: DOUBLE
      >
    >,
    attributes: MAP<STRING, STRING>,
    flags: INT
  >,
  metadata MAP<STRING, STRING>,
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
  metric_schema_url STRING
)
USING DELTA
COMMENT 'Reference column layout only; actual table owned by MLflow UC trace linking';
