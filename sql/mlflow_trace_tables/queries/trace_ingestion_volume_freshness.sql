-- Daily distinct trace counts and row volumes (spans + logs).
-- For max timestamps see trace_ingestion_max_timestamps.sql.

WITH span_daily AS (
  SELECT
    DATE_TRUNC('DAY', TIMESTAMP_MILLIS(CAST(start_time_unix_nano / 1000000 AS BIGINT))) AS day,
    COUNT(DISTINCT trace_id) AS distinct_trace_ids,
    COUNT(*) AS span_rows
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans`
  GROUP BY DATE_TRUNC('DAY', TIMESTAMP_MILLIS(CAST(start_time_unix_nano / 1000000 AS BIGINT)))
),

log_daily AS (
  SELECT
    DATE_TRUNC('DAY', TIMESTAMP_MILLIS(CAST(time_unix_nano / 1000000 AS BIGINT))) AS day,
    COUNT(DISTINCT trace_id) AS distinct_trace_ids,
    COUNT(*) AS log_rows
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
  WHERE trace_id IS NOT NULL AND TRIM(trace_id) != ''
  GROUP BY DATE_TRUNC('DAY', TIMESTAMP_MILLIS(CAST(time_unix_nano / 1000000 AS BIGINT)))
),

days AS (
  SELECT day FROM span_daily
  UNION
  SELECT day FROM log_daily
)

SELECT
  d.day,
  COALESCE(s.distinct_trace_ids, 0) AS span_table_distinct_traces,
  COALESCE(s.span_rows, 0) AS span_rows,
  COALESCE(l.distinct_trace_ids, 0) AS log_table_distinct_traces,
  COALESCE(l.log_rows, 0) AS log_rows
FROM days d
LEFT JOIN span_daily s ON d.day = s.day
LEFT JOIN log_daily l ON d.day = l.day
ORDER BY d.day DESC;
