from google.adk.agents import LlmAgent


def build_clarifier_agent(model_name: str) -> LlmAgent:
    return LlmAgent(
        name="Agent1_Clarifier",
        model=model_name,
        instruction=(
            "You are Agent 1. The user asked: {user_question?}\n"
            "The documentation directory is {documents_dir?}. "
            "Do not ask for the folder location or file names.\n"
            "If you need clarification to begin, ask concise questions "
            "about the question itself, not file locations. "
            "If clarification answers exist in {clarification_answers?}, use them.\n"
            "Return JSON with fields: "
            "clarifying_questions (list of strings), "
            "refined_question (string), "
            "notes (string).\n"
            "If no clarification is needed, return an empty list."
        ),
        output_key="clarification",
    )
