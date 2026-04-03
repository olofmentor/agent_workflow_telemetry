"""
Databricks MLflow + Unity Catalog tracing bootstrap.

Creates the experiment (if missing), links UC trace storage (creates OTEL tables
if they do not exist), then updates ``os.environ`` so OTLP exporters use the
experiment and spans table header.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from pathlib import Path

from observability.otlp_headers import merge_otel_header_string, parse_otel_headers

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TraceInfrastructureResult:
    experiment_id: str
    experiment_name: str | None
    full_otel_spans_table_name: str
    full_otel_logs_table_name: str


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_otel_traces_endpoint(environ: dict[str, str]) -> str | None:
    host = environ.get("DATABRICKS_HOST", "").strip().rstrip("/")
    if not host:
        return None
    return f"{host}/api/2.0/otel/v1/traces"


def _resolve_token(
    explicit: str | None,
    environ: dict[str, str],
) -> str | None:
    if explicit:
        return explicit
    t = environ.get("DATABRICKS_TOKEN", "").strip()
    if t:
        return t
    raw = environ.get("OTEL_EXPORTER_OTLP_HEADERS", "")
    if not raw.strip():
        return None
    h = parse_otel_headers(raw)
    auth = h.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth.split(None, 1)[1].strip()
    return None


def build_trace_configuration_updates(
    result: TraceInfrastructureResult,
    *,
    token: str | None = None,
    databricks_host: str | None = None,
    environ: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Pure: compute ``os.environ`` key/value updates for OTLP + MLflow (no mutation).

    Pass ``environ`` as a snapshot (e.g. ``dict(os.environ)``) for reproducible
    dry-runs; defaults to ``os.environ``.
    """
    snap = dict(environ) if environ is not None else dict(os.environ)
    if databricks_host:
        snap = {**snap, "DATABRICKS_HOST": databricks_host.strip().rstrip("/")}

    tok = _resolve_token(token, snap)
    if not tok:
        raise ValueError(
            "No token: set DATABRICKS_TOKEN or Authorization=Bearer... in OTEL_EXPORTER_OTLP_HEADERS"
        )

    updates: dict[str, str] = {}
    if databricks_host:
        updates["DATABRICKS_HOST"] = databricks_host.strip().rstrip("/")

    endpoint = snap.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not endpoint:
        derived = _default_otel_traces_endpoint(snap) or ""
        if derived:
            updates["OTEL_EXPORTER_OTLP_ENDPOINT"] = derived
            endpoint = derived

    effective_endpoint = (
        updates.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")
        or snap.get("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    )
    if not effective_endpoint:
        raise ValueError(
            "OTEL_EXPORTER_OTLP_ENDPOINT is empty and DATABRICKS_HOST is not set; "
            "set one of them so traces can be exported."
        )

    merged = merge_otel_header_string(
        snap.get("OTEL_EXPORTER_OTLP_HEADERS", ""),
        {
            "Authorization": f"Bearer {tok}",
            "x-mlflow-experiment-id": result.experiment_id,
            "X-Databricks-UC-Table-Name": result.full_otel_spans_table_name,
        },
    )
    updates["OTEL_EXPORTER_OTLP_HEADERS"] = merged
    updates["MLFLOW_EXPERIMENT_ID"] = result.experiment_id
    return updates


def apply_trace_configuration(
    result: TraceInfrastructureResult,
    *,
    token: str | None = None,
    databricks_host: str | None = None,
    update_environ: bool = True,
    verbose: bool = True,
) -> dict[str, str]:
    """
    Build OTLP/MLflow env updates and optionally apply them to ``os.environ``.

    Returns the dict of applied updates (same keys as ``build_trace_configuration_updates``).
    """
    updates = build_trace_configuration_updates(
        result,
        token=token,
        databricks_host=databricks_host,
        environ=dict(os.environ),
    )
    if verbose:
        logger.info(
            "Trace configuration: OTEL_EXPORTER_OTLP_ENDPOINT=%s (merged headers and experiment id updated)",
            updates.get("OTEL_EXPORTER_OTLP_ENDPOINT", os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "")),
        )
        logger.info("x-mlflow-experiment-id=%s", result.experiment_id)
        logger.info("X-Databricks-UC-Table-Name=%s", result.full_otel_spans_table_name)
    if update_environ:
        os.environ.update(updates)
    return updates


def ensure_trace_infrastructure(
    *,
    warehouse_id: str | None = None,
    catalog: str | None = None,
    schema: str | None = None,
    experiment_name: str | None = None,
    experiment_id: str | None = None,
    verbose: bool = True,
) -> TraceInfrastructureResult:
    """
    Ensure an MLflow experiment exists and UC OTEL tables exist for it.

    Calls MLflow ``set_experiment_trace_location`` (Databricks), which creates
    Unity Catalog tables when needed.
    """
    warehouse_id = warehouse_id or os.getenv("MLFLOW_TRACING_SQL_WAREHOUSE_ID", "").strip()
    if not warehouse_id:
        raise ValueError(
            "MLFLOW_TRACING_SQL_WAREHOUSE_ID is required (SQL warehouse id from Databricks URL)."
        )

    catalog = (catalog or os.getenv("DATABRICKS_CATALOG", "main")).strip()
    schema = (schema or os.getenv("DATABRICKS_SCHEMA", "mlflow_traces")).strip()
    experiment_id = (experiment_id or os.getenv("MLFLOW_EXPERIMENT_ID", "") or "").strip() or None
    experiment_name = (
        experiment_name or os.getenv("MLFLOW_EXPERIMENT_NAME", "/Shared/agent_traces").strip()
    )

    try:
        import mlflow
        from mlflow.entities import UCSchemaLocation
        from mlflow.tracing.enablement import set_experiment_trace_location
    except ImportError as e:
        raise ImportError(
            "Install mlflow for Databricks tracing: pip install 'mlflow[databricks]>=3.6.0'"
        ) from e

    mlflow.set_tracking_uri("databricks")
    os.environ["MLFLOW_TRACING_SQL_WAREHOUSE_ID"] = warehouse_id

    if experiment_id:
        if verbose:
            logger.info("Using experiment ID: %s", experiment_id)
    else:
        if verbose:
            logger.info("Resolving experiment: %s", experiment_name)
        exp = mlflow.get_experiment_by_name(experiment_name)
        if exp is not None:
            experiment_id = exp.experiment_id
            if verbose:
                logger.info("Found experiment ID: %s", experiment_id)
        else:
            experiment_id = mlflow.create_experiment(name=experiment_name)
            if verbose:
                logger.info("Created experiment ID: %s", experiment_id)

    assert experiment_id is not None

    if verbose:
        logger.info(
            "Linking experiment to UC schema: %s.%s (tables created if missing)",
            catalog,
            schema,
        )
    uc = set_experiment_trace_location(
        location=UCSchemaLocation(catalog_name=catalog, schema_name=schema),
        experiment_id=experiment_id,
        sql_warehouse_id=warehouse_id,
    )

    if verbose:
        logger.info("OK: spans table: %s", uc.full_otel_spans_table_name)
        logger.info("OK: logs table: %s", uc.full_otel_logs_table_name)

    return TraceInfrastructureResult(
        experiment_id=experiment_id,
        experiment_name=experiment_name,
        full_otel_spans_table_name=uc.full_otel_spans_table_name,
        full_otel_logs_table_name=uc.full_otel_logs_table_name,
    )


# Backwards-compatible name
def apply_otel_environment(
    result: TraceInfrastructureResult,
    *,
    token: str | None = None,
    databricks_host: str | None = None,
    verbose: bool = True,
) -> None:
    """Write MLflow/UC connection into ``os.environ`` for OTLP setup."""
    apply_trace_configuration(
        result,
        token=token,
        databricks_host=databricks_host,
        update_environ=True,
        verbose=verbose,
    )


def init_and_connect(
    *,
    warehouse_id: str | None = None,
    catalog: str | None = None,
    schema: str | None = None,
    experiment_name: str | None = None,
    experiment_id: str | None = None,
    token: str | None = None,
    databricks_host: str | None = None,
    verbose: bool = True,
    update_environ: bool = True,
    dry_run: bool = False,
) -> TraceInfrastructureResult:
    """
    One-shot: UC tables (if needed) + experiment + OTEL env for the agent.

    With ``dry_run=True``, runs MLflow ensure steps then only logs planned
    ``os.environ`` updates without applying them.
    """
    result = ensure_trace_infrastructure(
        warehouse_id=warehouse_id,
        catalog=catalog,
        schema=schema,
        experiment_name=experiment_name,
        experiment_id=experiment_id,
        verbose=verbose,
    )
    if dry_run:
        updates = build_trace_configuration_updates(
            result,
            token=token,
            databricks_host=databricks_host,
            environ=dict(os.environ),
        )
        if verbose:
            masked = {
                k: ("<redacted>" if "HEADERS" in k or "TOKEN" in k.upper() else v)
                for k, v in updates.items()
            }
            logger.info("Dry-run: planned environ updates: %s", masked)
        return result
    if update_environ:
        apply_trace_configuration(
            result,
            token=token,
            databricks_host=databricks_host,
            update_environ=True,
            verbose=verbose,
        )
    return result


def load_env_from_project_root() -> None:
    """Load ``.env`` from the repository root (for ``python -m init``)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(_project_root() / ".env")
