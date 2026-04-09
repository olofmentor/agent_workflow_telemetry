-- View: mlflow_experiment_trace_unified
-- Captured from: DESCRIBE TABLE EXTENDED dev_ai.agent_traces.mlflow_experiment_trace_unified (View Text)
-- Replace catalog/schema in identifiers if you recreate this view elsewhere.
-- Root-span predicate normalized to Spark empty string literal (DESCRIBE showed quoted empty).

CREATE OR REPLACE VIEW dev_ai.agent_traces.mlflow_experiment_trace_unified AS
WITH
-- 1. Extract trace metadata from trace metadata events
trace_metadata AS (
  SELECT
    trace_id,
    PARSE_JSON(body) AS metadata_data
  FROM
    `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
  WHERE
    event_name = 'genai.trace.metadata'
),
-- 2. Extract and aggregate individual tag events (handling duplicates by taking the most recent)
tags_agg AS (
  SELECT
    trace_id,
    MAP_FROM_ENTRIES(
      COLLECT_LIST(
        STRUCT(
          key,
          value
        )
      )
    ) AS tags
  FROM (
    SELECT
      trace_id,
      PARSE_JSON(body):key::STRING AS key,
      PARSE_JSON(body):value::STRING AS value,
      ROW_NUMBER() OVER (
        PARTITION BY trace_id, PARSE_JSON(body):key::STRING
        ORDER BY time_unix_nano DESC
      ) AS rn
    FROM
      `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
    WHERE
      event_name = 'genai.trace.tag'
  ) tag_events
  WHERE tag_events.rn = 1
  GROUP BY
    tag_events.trace_id
),
-- 3. Extract the root span which contains the full request/response and trace-level info
root_span AS (
  SELECT
    trace_id,
    span_id,
    name,
    TIMESTAMP_MILLIS(CAST(start_time_unix_nano / 1000000 AS BIGINT)) AS request_time,
    CASE
      WHEN status.code = 'STATUS_CODE_OK' OR status.code IS NULL THEN 'OK' -- Convert from OTEL status code semantics to the MLflow status code
      WHEN status.code = 'STATUS_CODE_ERROR' THEN 'ERROR'
      ELSE status.code
    END AS state,
    (end_time_unix_nano - start_time_unix_nano) / 1000000.0 AS execution_duration_ms,
    COALESCE(
      attributes['mlflow.spanInputs'],
      attributes['input.value'],
      attributes['traceloop.entity.input'],
      attributes['gen_ai.input.messages'],
      attributes['gcp.vertex.agent.llm_request'],
      attributes['gcp.vertex.agent.tool_call_args']
    ) AS request,
    COALESCE(
      attributes['mlflow.spanOutputs'],
      attributes['output.value'],
      attributes['traceloop.entity.output'],
      attributes['gen_ai.output.messages'],
      attributes['gcp.vertex.agent.llm_response'],
      attributes['gcp.vertex.agent.tool_response']
    ) AS response
  FROM
    `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans`
  WHERE
    COALESCE(parent_span_id, '') = ''  -- Root span has empty parent
),
-- 4. Aggregate all spans grouped by trace_id
spans_agg AS (
  SELECT
    trace_id,
    COLLECT_LIST(STRUCT(*)) AS spans
  FROM
    `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_spans`
  GROUP BY
    trace_id
),
-- 5. Aggregated valid assessments grouped by trace_id
assessments_agg AS (
  SELECT
    trace_id,
    COLLECT_LIST(parse_json(body)) AS assessments
  FROM
    (
    SELECT
      trace_id,
      body,
      attributes['deleted'] AS is_deleted,
      attributes['assessment_id'] AS assessment_id,
      ROW_NUMBER() OVER (
        PARTITION BY attributes['assessment_id']
        ORDER BY time_unix_nano DESC
      ) AS rn
    FROM
      `dev_ai`.`agent_traces`.`mlflow_experiment_trace_otel_logs`
    WHERE
      event_name = 'genai.assessments.snapshot'  -- Update event name as needed
    ) assessment_events
  WHERE
    assessment_events.rn = 1 AND assessment_events.is_deleted != 'true'
  GROUP BY
    assessment_events.trace_id
)
-- 6. Main query - join the trace data from spans with metadata, tags, and assessments
SELECT
  rs.trace_id,
  tm.metadata_data:client_request_id::STRING AS client_request_id,
  rs.request_time,
  rs.state,
  rs.execution_duration_ms,
  rs.request,
  rs.response,
  COALESCE(tm.metadata_data:trace_metadata::MAP<STRING, STRING>, MAP()) AS trace_metadata,
  COALESCE(ta.tags, MAP()) AS tags,
  sa.spans,
  COALESCE(
    TRANSFORM(
      aa.assessments,
      body -> STRUCT(
        body:assessment_id::STRING AS assessment_id,
        body:trace_id::STRING AS trace_id,
        body:assessment_name::STRING AS assessment_name,
        FROM_JSON(body:source::STRING, 'STRUCT<source_id: STRING, source_type: STRING>') AS source,
        TIMESTAMP_MILLIS(CAST(body:create_time::DOUBLE AS BIGINT)) AS create_time,
        TIMESTAMP_MILLIS(CAST(body:last_update_time::DOUBLE AS BIGINT)) AS last_update_time,
        FROM_JSON(
            body:expectation::STRING,
            'STRUCT<
                value: STRING,
                serialized_value: STRUCT<serialization_format: STRING, value: STRING, stack_trace: STRING>
            >'
        ) AS expectation,
        FROM_JSON(
            body:feedback::STRING,
            'STRUCT<
                value: STRING,
                error: STRUCT<error_code: STRING, error_message: STRING, stack_trace: STRING>
            >'
        ) AS feedback,
        body:rationale::STRING AS rationale,
        FROM_JSON(body:metadata::STRING, 'MAP<STRING, STRING>') AS metadata,
        body:span_id::STRING AS span_id,
        body:overrides::STRING AS overrides,
        body:valid::STRING AS valid
      )
    ),
    ARRAY()
  ) AS assessments
FROM
  root_span rs
  LEFT JOIN trace_metadata tm ON rs.trace_id = tm.trace_id
  LEFT JOIN tags_agg ta ON rs.trace_id = ta.trace_id
  LEFT JOIN assessments_agg aa ON rs.trace_id = aa.trace_id
  LEFT JOIN spans_agg sa ON rs.trace_id = sa.trace_id;
