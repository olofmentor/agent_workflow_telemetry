"""ADK `after_model_callback` helpers (keyword args: callback_context, llm_response)."""

from __future__ import annotations

from typing import Any, Callable

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import AfterModelCallback
from google.adk.models.llm_response import LlmResponse

from observability.session_logs import log_llm_step_completed


def after_model_logging(output_state_key: str) -> Callable[..., Any]:
    """Return an ADK ``after_model_callback`` that logs the step (returns ``None``)."""

    def _cb(
        *,
        callback_context: CallbackContext,
        llm_response: LlmResponse,
    ) -> None:
        log_llm_step_completed(output_state_key, callback_context, llm_response)
        return None

    return _cb


def merge_after_model_callbacks(
    first: AfterModelCallback,
    second: AfterModelCallback | None,
) -> AfterModelCallback:
    """Prepend logging (or any `first` callback) before optional user callback(s).

    ADK runs callbacks in order; the first callback that returns a non-None
    ``LlmResponse`` replaces the model output. Logging callbacks should return
    ``None``.
    """
    if second is None:
        return first
    if isinstance(second, list):
        return [first, *second]
    return [first, second]


def build_instrumented_llm_agent(
    *, output_key: str, after_model_callback: AfterModelCallback | None = None, **llm_kwargs: Any
) -> LlmAgent:
    """Return ``LlmAgent`` with session logging always wired on ``after_model``.

    Pass ``after_model_callback`` to add your own handler(s); logging runs
    first. For new agents, prefer this over raw ``LlmAgent`` so OTLP logs stay
    consistent.
    """
    log_cb = after_model_logging(output_key)
    merged = merge_after_model_callbacks(log_cb, after_model_callback)
    return LlmAgent(
        output_key=output_key,
        after_model_callback=merged,
        **llm_kwargs,
    )
