from adk_templates import instrumented_llm_agent


def build_synthesizer_agent(model_name: str):
    return instrumented_llm_agent(
        name="Agent3_Synthesizer",
        model=model_name,
        output_key="final_answer",
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
    )
