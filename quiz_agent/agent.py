from google.adk.agents import LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.adk.runners import Runner
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.agents.callback_context import CallbackContext

from .function_tools import (
    get_quiz_questions,
    start_quiz,
    submit_answer,
    get_current_question,
    get_quiz_status,
    reset_quiz,
)

from .agent_tools import youtube_agent, diagram_agent

from .prompts import quiz_instructions
from .agent_utils import initialize_quiz_state, retry_config


from google.genai import types
from typing import Optional



# Callback to initialize quiz state
# https://google.github.io/adk-docs/callbacks/types-of-callbacks/#before-agent-callback
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Initialize quiz state if not already present"""
    initialize_quiz_state(callback_context.state)
    return None


# The initial agent
root_agent = LlmAgent(
    name='QuizAgent',
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
    ),
    description='A helpful quiz master with a theoretical knowledge of guitar playing.',
    instruction=quiz_instructions,
    tools=[get_quiz_questions, 
           start_quiz, 
           submit_answer, 
           get_current_question, 
           get_quiz_status, 
           reset_quiz,
           AgentTool(agent=youtube_agent),
           AgentTool(agent=diagram_agent),
    ],
)


# The app
quiz_agent_app = App(
    name="QuizAgentApp",
    root_agent=root_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=5,
        overlap_size=1,
    )
)


# Database URL and service for storing session data - Using asynchronous sqlite
db_url = "sqlite+aiosqlite:///session_data.db"
session_service = DatabaseSessionService(db_url=db_url)


# The runner of the agent
runner = Runner(
    app=quiz_agent_app,
    session_service=session_service,
)
