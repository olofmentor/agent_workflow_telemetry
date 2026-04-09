-- View: mlflow_experiment_trace_metadata
-- Captured from: DESCRIBE TABLE EXTENDED dev_ai.agent_traces.mlflow_experiment_trace_metadata (View Text)
-- Replace catalog/schema in identifiers if you recreate this view elsewhere.

CREATE OR REPLACE VIEW dev_ai.agent_traces.mlflow_experiment_trace_metadata AS
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
-- 3. Aggregated assessments grouped by trace_id (filtering on deleted attribute)
assessments_agg AS (
  SELECT
    trace_id,
    COLLECT_LIST(PARSE_JSON(body)) AS assessments
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
      event_name = 'genai.assessments.snapshot'
    ) assessment_events
  WHERE
    assessment_events.rn = 1 AND assessment_events.is_deleted != 'true'
  GROUP BY
    assessment_events.trace_id
)
-- 4. Main query - join metadata with tags and assessments
SELECT
  tm.trace_id,
  tm.metadata_data:client_request_id::STRING AS client_request_id,
  COALESCE(ta.tags, MAP()) AS tags,
  COALESCE(tm.metadata_data:trace_metadata::MAP<STRING, STRING>, MAP()) AS trace_metadata,
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
  trace_metadata tm
  LEFT JOIN tags_agg ta ON tm.trace_id = ta.trace_id
  LEFT JOIN assessments_agg aa ON tm.trace_id = aa.trace_id;
