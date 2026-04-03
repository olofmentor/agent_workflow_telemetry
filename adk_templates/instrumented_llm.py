"""Template factory for :class:`google.adk.agents.LlmAgent` with OTLP session logging."""

from observability.llm_callbacks import build_instrumented_llm_agent as instrumented_llm_agent

__all__ = ["instrumented_llm_agent"]
