from google.adk.agents import LlmAgent


def build_summarizer_agent(model_name: str) -> LlmAgent:
    return LlmAgent(
        name="Agent1_FileSummarizer",
        model=model_name,
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
        output_key="file_summaries",
    )
