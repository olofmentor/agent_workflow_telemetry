from typing import AsyncGenerator

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event


class UserQuestionBootstrapAgent(BaseAgent):
    name: str = "Agent0_UserQuestionBootstrap"
    description: str = "Stores the latest user message as user_question."
    documents_dir: str = "./input_files"

    @staticmethod
    def _extract_text(event: Event) -> str:
        if not event.content or not event.content.parts:
            return ""
        chunks: list[str] = []
        for part in event.content.parts:
            text = getattr(part, "text", None)
            if text:
                chunks.append(text)
        return "\n".join(chunks).strip()

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        if ctx.session.state.get("user_question"):
            yield Event(author=self.name)
            return

        user_text = ""
        for event in reversed(ctx.session.events):
            if event.author != "user":
                continue
            user_text = self._extract_text(event)
            if user_text:
                break

        ctx.session.state["user_question"] = user_text
        ctx.session.state["documents_dir"] = self.documents_dir
        yield Event(author=self.name)
