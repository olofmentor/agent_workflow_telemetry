"""Session-correlated stdlib logging (exported via OTLP LoggingHandler → Unity Catalog)."""

from __future__ import annotations

import logging
import os

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.invocation_context import InvocationContext
from google.adk.models.llm_response import LlmResponse
from google.genai import types

logger = logging.getLogger(__name__)

_DEFAULT_MAX_CHARS = 256000


def max_response_log_chars() -> int:
    raw = os.environ.get("AGENT_LOG_RESPONSE_MAX_CHARS")
    if raw is None or raw == "":
        return _DEFAULT_MAX_CHARS
    return max(4096, int(raw))


def _maybe_truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n... [truncated, total_chars={len(text)}]"


def split_model_visible_and_reasoning_text(
    content: types.Content | None,
) -> tuple[str, str]:
    """Split response text into user-visible vs model reasoning (thought parts)."""
    if not content or not content.parts:
        return "", ""

    visible: list[str] = []
    reasoning: list[str] = []
    for part in content.parts:
        if not part.text:
            continue
        if isinstance(part.thought, bool) and part.thought:
            reasoning.append(part.text)
        else:
            visible.append(part.text)
    return "\n".join(visible).strip(), "\n".join(reasoning).strip()


def log_llm_step_completed(
    output_state_key: str,
    ctx: CallbackContext,
    response: LlmResponse,
) -> None:
    """Log one LLM turn with session/invocation ids and optional reasoning text."""
    visible, reasoning = split_model_visible_and_reasoning_text(response.content)
    limit = max_response_log_chars()
    visible_logged = _maybe_truncate(visible, limit)
    reasoning_logged = _maybe_truncate(reasoning, limit) if reasoning else ""

    um = response.usage_metadata
    in_tok = getattr(um, "prompt_token_count", None) if um else None
    out_tok = getattr(um, "candidates_token_count", None) if um else None
    reasoning_tok = getattr(um, "thoughts_token_count", None) if um else None
    finish = (
        str(response.finish_reason) if response.finish_reason is not None else None
    )

    logger.info(
        "LLM step completed",
        extra={
            "event_type": "agent.llm_step",
            "session_id": ctx.session.id,
            "invocation_id": ctx.invocation_id,
            "agent_name": ctx.agent_name,
            "output_state_key": output_state_key,
            "finish_reason": finish,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
            "reasoning_token_count": reasoning_tok,
            "response_char_count": len(visible),
            "reasoning_char_count": len(reasoning),
            "model_response_text": visible_logged,
            "model_reasoning_text": reasoning_logged or None,
        },
    )


def log_custom_agent_step(kind: str, ctx: InvocationContext, detail: str) -> None:
    """Log completion of a non-LLM agent step (reader, bootstrap, etc.)."""
    logger.info(
        "%s",
        detail,
        extra={
            "event_type": f"agent.{kind}",
            "session_id": ctx.session.id,
            "invocation_id": ctx.invocation_id,
            "agent_name": ctx.agent.name,
        },
    )
