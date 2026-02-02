from google.adk.agents import LlmAgent


def build_synthesizer_agent(model_name: str) -> LlmAgent:
    return LlmAgent(
        name="Agent3_Synthesizer",
        model=model_name,
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
        output_key="final_answer",
    )
