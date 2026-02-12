import logging
from google.adk.agents import SequentialAgent

from .agents.bootstrap import UserQuestionBootstrapAgent
from .agents.clarifier import build_clarifier_agent
from .agents.reader import DocumentReaderAgent
from .agents.summarizer import build_summarizer_agent
from .agents.synthesizer import build_synthesizer_agent
from .config import load_config

# Setup logger for workflow
logger = logging.getLogger(__name__)


def build_workflow() -> SequentialAgent:
    logger.info("Building LessonsLearnedWorkflow")
    config = load_config()

    logger.info(f"Initializing agents with model: {config.model_name}")
    agent0_bootstrap = UserQuestionBootstrapAgent(
        documents_dir=config.documents_dir
    )
    agent1_clarify = build_clarifier_agent(config.model_name)
    agent2_reader = DocumentReaderAgent(
        documents_dir=config.documents_dir,
        max_file_chars=config.max_file_chars,
        preview_chars=config.preview_chars,
        prefer_previews=config.prefer_previews,
    )
    agent1_summarize = build_summarizer_agent(config.model_name)
    agent3_synthesize = build_synthesizer_agent(config.model_name)

    logger.info("Workflow agents initialized successfully")
    return SequentialAgent(
        name="LessonsLearnedWorkflow",
        sub_agents=[
            agent0_bootstrap,
            agent1_clarify,
            agent2_reader,
            agent1_summarize,
            agent3_synthesize,
        ],
    )


root_agent = build_workflow()
