-- Interleaved OTLP logs and spans for one trace_id (paste param).
-- Avoids cartesian join: one row per log row and one row per span; sort by t_nano.

WITH params AS (
  SELECT 'REPLACE_WITH_TRACE_ID' AS trace_id
),

combined AS (
  SELECT
    'log' AS row_kind,
    l.time_unix_nano AS t_nano,
    l.trace_id,
    l.span_id,
    CAST(NULL AS STRING) AS parent_span_id,
    l.event_name AS step_name,
    l.severity_text,
    l.body,
    CAST(NULL AS DOUBLE) AS duration_ms,
    l.attributes AS attributes
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs` l
  CROSS JOIN params p
  WHERE l.trace_id = p.trace_id

  UNION ALL

  SELECT
    'span',
    s.start_time_unix_nano,
    s.trace_id,
    s.span_id,
    s.parent_span_id,
    s.name,
    CAST(NULL AS STRING),
    CAST(NULL AS STRING),
    ROUND((s.end_time_unix_nano - s.start_time_unix_nano) / 1000000.0, 3),
    s.attributes
  FROM `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans` s
  CROSS JOIN params p
  WHERE s.trace_id = p.trace_id
)

SELECT *
FROM combined
ORDER BY t_nano ASC, row_kind ASC;
