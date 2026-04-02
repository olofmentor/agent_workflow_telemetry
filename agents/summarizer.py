from google.adk.agents import LlmAgent

from .step_logging import log_llm_step_completed


def build_summarizer_agent(model_name: str) -> LlmAgent:
    _OUT = "file_summaries"

    def _after_model(ctx=None, response=None, **kwargs):
        ctx = kwargs.get("callback_context", ctx)
        response = kwargs.get("llm_response", response)
        if ctx is None or response is None:
            return None
        log_llm_step_completed(_OUT, ctx, response)
        return None

    return LlmAgent(
        name="Agent1_FileSummarizer",
        model=model_name,
        after_model_callback=_after_model,
        instruction=(
            "You are Agent 1. Summarize each file for the user's question.\n"
            "User question: {user_question?}\n"
            "Clarification output: {clarification}\n"
            "Documents JSON: {documents_json}\n"
            "Documents manifest: {documents_manifest}\n"
            "Documents preview: {documents_preview}\n"
            "Process all files in the documents JSON without asking for file "
            "names or paths. For each document, provide: file, summary, "
            "key_points, and note if content is unavailable.\n"
            "Return JSON list of objects in the same order as documents_json."
        ),
        output_key=_OUT,
    )
