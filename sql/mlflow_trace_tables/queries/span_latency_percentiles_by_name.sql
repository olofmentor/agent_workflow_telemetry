-- Latency distribution by span name and day (milliseconds).
-- Databricks / Spark: approx_percentile; tune accuracy if needed.

WITH span_durations AS (
  SELECT
    name AS span_name,
    DATE_TRUNC('DAY', TIMESTAMP_MILLIS(CAST(start_time_unix_nano / 1000000 AS BIGINT))) AS day,
    (end_time_unix_nano - start_time_unix_nano) / 1000000.0 AS duration_ms
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans`
  WHERE end_time_unix_nano >= start_time_unix_nano
    AND end_time_unix_nano IS NOT NULL
    AND start_time_unix_nano IS NOT NULL
)

SELECT
  day,
  span_name,
  COUNT(*) AS span_count,
  ROUND(AVG(duration_ms), 3) AS avg_ms,
  ROUND(MIN(duration_ms), 3) AS min_ms,
  ROUND(MAX(duration_ms), 3) AS max_ms,
  ROUND(approx_percentile(duration_ms, 0.5), 3) AS p50_ms,
  ROUND(approx_percentile(duration_ms, 0.95), 3) AS p95_ms
FROM span_durations
GROUP BY day, span_name
ORDER BY day DESC, span_count DESC;
