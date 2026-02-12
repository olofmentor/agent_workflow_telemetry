# Multi-agent lessons learned workflow (Google ADK)

This repo defines a sequential multi-agent workflow using Google ADK, following
the multi-agent patterns described in the ADK docs:
https://google.github.io/adk-docs/agents/multi-agents/

## What it does

The workflow is sequential and uses three logical agents:

1. **Agent 1 (Clarifier)** receives the user question and asks for any needed
   clarifications to start the workflow.
2. **Agent 2 (Document Reader)** reads every file in a documentation directory
   and stores their contents in shared session state.
3. **Agent 1 (File Summarizer)** summarizes each document with key points that
   help answer the question.
4. **Agent 3 (Synthesizer)** creates:
   - an executive summary,
   - a longer summary,
   - references to the documents used.

## Project structure

- `agent.py` exposes `root_agent`/`app` for ADK CLI usage.
- `workflow.py` wires the agents into a sequential workflow.
- `config.py` centralizes environment configuration and path normalization.
- `agents/` contains reader, clarifier, summarizer, and synthesizer agents.
- `tests/` contains workflow and OTLP export tests.
- `scripts/` contains Databricks utility scripts (see scripts/README.md).
- `input_files/` holds project documentation to summarize.

## Configuration

The workflow expects these environment variables:

- `MODEL` (default: `gemini-2.0-flash`)
- `DOCUMENTS_DIR` (default: `./input_files`)
- `MAX_FILE_CHARS` (default: `12000`)
- `OPENAI_API_BASE` (for LM Studio / Azure Foundry, e.g. `http://localhost:1234/v1`)
- `OPENAI_API_KEY` (for LM Studio / Azure Foundry)
## Document support

- Text formats: `.md`, `.txt`, `.rst`, `.log`, `.csv`, `.json`, `.yaml`, `.yml`
- PDFs: `.pdf` (text-based PDFs only; scanned PDFs may extract no text)


## Using the workflow

1. Put your project documentation in `./input_files` (or set `DOCUMENTS_DIR`).
2. Install dependencies: `pip install -r requirements.txt`.
3. Configure OpenTelemetry for MLflow tracing (see [MLflow + Google ADK](https://mlflow.org/docs/latest/genai/tracing/integrations/listing/google-adk/)):
   - `OTEL_EXPORTER_OTLP_ENDPOINT` – OTLP endpoint URL
   - `OTEL_EXPORTER_OTLP_HEADERS` – headers (e.g. `x-mlflow-experiment-id=<id>`)
4. From the parent directory of this repo, run `adk run SE_workflow_test`.
5. Provide the user question as the initial message.
6. If the clarifier asks questions, pass your answers by setting
   `clarification_answers` in session state before re-running the workflow.

### Databricks MLflow

For Databricks, set:

- `OTEL_EXPORTER_OTLP_ENDPOINT="https://<workspace>/api/2.0/otel/v1/traces"`
- `OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer <token>,x-mlflow-experiment-id=<id>"`

Create the experiment in Databricks if needed, then use its ID in the header.

The workflow stores intermediate outputs in session state:

- `clarification`
- `documents`
- `documents_json`
- `file_summaries`
- `final_answer`

## LM Studio (local LLM)

To run a local model via LM Studio (OpenAI-compatible API), set:

- `MODEL="openai/<model-name>"` (e.g., `openai/llama-3.1-8b-instruct`)
- `OPENAI_API_BASE="http://localhost:1234/v1"`
- `OPENAI_API_KEY="lm-studio"`

LM Studio must be running with the local server enabled.

