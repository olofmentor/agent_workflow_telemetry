from adk_templates import instrumented_llm_agent


def build_summarizer_agent(model_name: str):
    return instrumented_llm_agent(
        name="Agent1_FileSummarizer",
        model=model_name,
        output_key="file_summaries",
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
    )
