-- Latest timestamps in OTEL span and log tables (ingestion freshness).
-- Pair with trace_ingestion_volume_freshness.sql.

SELECT
  TIMESTAMP_MILLIS(
    CAST((SELECT MAX(start_time_unix_nano) FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans`) / 1000000 AS BIGINT)
  ) AS latest_span_start_time,
  TIMESTAMP_MILLIS(
    CAST((SELECT MAX(time_unix_nano) FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`) / 1000000 AS BIGINT)
  ) AS latest_log_time;
