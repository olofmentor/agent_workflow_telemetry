from __future__ import annotations

from typing import Any

from google.adk.plugins.base_plugin import BasePlugin
from google.genai import types

from .core import TelemetryEvent, TelemetrySink


def _content_to_text(content: types.Content | None) -> str:
    if not content or not content.parts:
        return ""
    chunks: list[str] = []
    for part in content.parts:
        text = getattr(part, "text", None)
        if text:
            chunks.append(text)
    return "\n".join(chunks).strip()


class ActionLoggingPlugin(BasePlugin):
    def __init__(self, sink: TelemetrySink, name: str = "action_logger"):
        super().__init__(name=name)
        self.sink = sink

    async def on_user_message_callback(
        self, *, invocation_context, user_message: types.Content
    ):
        self.sink.record(
            TelemetryEvent(
                name="user_message",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "user_id": invocation_context.session.user_id,
                    "content": _content_to_text(user_message),
                },
            )
        )
        return None

    async def on_event_callback(self, *, invocation_context, event):
        content_text = ""
        if getattr(event, "content", None):
            content_text = _content_to_text(event.content)
        self.sink.record(
            TelemetryEvent(
                name="event",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "user_id": invocation_context.session.user_id,
                    "author": getattr(event, "author", ""),
                    "event_id": getattr(event, "id", ""),
                    "content": content_text,
                },
            )
        )
        return None

    async def before_agent_callback(self, *, agent, callback_context):
        invocation_context = callback_context._invocation_context
        self.sink.record(
            TelemetryEvent(
                name="before_agent",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "agent": agent.name,
                },
            )
        )
        return None

    async def after_agent_callback(self, *, agent, callback_context):
        invocation_context = callback_context._invocation_context
        self.sink.record(
            TelemetryEvent(
                name="after_agent",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "agent": agent.name,
                },
            )
        )
        return None

    async def before_tool_callback(
        self, *, tool, tool_args: dict[str, Any], tool_context
    ):
        self.sink.record(
            TelemetryEvent(
                name="before_tool",
                attributes={
                    "session_id": tool_context._invocation_context.session.id,
                    "app_name": tool_context._invocation_context.session.app_name,
                    "tool": tool.name,
                    "tool_args": tool_args,
                },
            )
        )
        return None

    async def after_tool_callback(
        self,
        *,
        tool,
        tool_args: dict[str, Any],
        tool_context,
        result: dict,
    ):
        self.sink.record(
            TelemetryEvent(
                name="after_tool",
                attributes={
                    "session_id": tool_context._invocation_context.session.id,
                    "app_name": tool_context._invocation_context.session.app_name,
                    "tool": tool.name,
                    "tool_args": tool_args,
                    "result": result,
                },
            )
        )
        return None

    async def before_model_callback(self, *, callback_context, llm_request):
        invocation_context = callback_context._invocation_context
        self.sink.record(
            TelemetryEvent(
                name="before_model",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "model": getattr(llm_request, "model", ""),
                },
            )
        )
        return None

    async def after_model_callback(self, *, callback_context, llm_response):
        invocation_context = callback_context._invocation_context
        self.sink.record(
            TelemetryEvent(
                name="after_model",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "model_version": getattr(llm_response, "model_version", ""),
                },
            )
        )
        return None

    async def on_tool_error_callback(self, *, tool, tool_args, tool_context, error):
        self.sink.record(
            TelemetryEvent(
                name="tool_error",
                attributes={
                    "session_id": tool_context._invocation_context.session.id,
                    "app_name": tool_context._invocation_context.session.app_name,
                    "tool": tool.name,
                    "tool_args": tool_args,
                    "error": str(error),
                },
            )
        )
        return None

    async def on_model_error_callback(self, *, callback_context, llm_request, error):
        invocation_context = callback_context._invocation_context
        self.sink.record(
            TelemetryEvent(
                name="model_error",
                attributes={
                    "session_id": invocation_context.session.id,
                    "app_name": invocation_context.session.app_name,
                    "model": getattr(llm_request, "model", ""),
                    "error": str(error),
                },
            )
        )
        return None
