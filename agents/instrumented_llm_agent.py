"""Template for LLM agents: always attach session/OTLP logging on each model turn.

Use :func:`instrumented_llm_agent` instead of constructing :class:`google.adk.agents.LlmAgent`
directly unless you intentionally skip structured logs. Reusable primitives live in the
``observability`` package.
"""

from observability.llm_callbacks import build_instrumented_llm_agent as instrumented_llm_agent

__all__ = ["instrumented_llm_agent"]
