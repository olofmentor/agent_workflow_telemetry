from google.adk.agents import LlmAgent

from .step_logging import log_llm_step_completed


def build_synthesizer_agent(model_name: str) -> LlmAgent:
    _OUT = "final_answer"

    def _after_model(ctx=None, response=None, **kwargs):
        ctx = kwargs.get("callback_context", ctx)
        response = kwargs.get("llm_response", response)
        if ctx is None or response is None:
            return None
        log_llm_step_completed(_OUT, ctx, response)
        return None

    return LlmAgent(
        name="Agent3_Synthesizer",
        model=model_name,
        after_model_callback=_after_model,
        instruction=(
            "You are Agent 3. Create the final response using the inputs.\n"
            "User question: {user_question?}\n"
            "Clarification output: {clarification}\n"
            "File summaries: {file_summaries}\n"
            "Documents manifest: {documents_manifest}\n"
            "Output three sections:\n"
            "1) Executive summary answering the question.\n"
            "2) Longer summary based on the file summaries.\n"
            "3) References: list of document paths used."
        ),
        output_key=_OUT,
    )
