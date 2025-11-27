from google.adk.agents import LlmAgent
from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions.database_session_service import DatabaseSessionService
from google.adk.agents.callback_context import CallbackContext
# from google.adk.tools import google_search
from .function_tools import (
    get_quiz_questions,
    start_quiz,
    submit_answer,
    get_current_question,
    get_quiz_status,
    reset_quiz,
)

from .prompts import quiz_instructions
from .agent_utils import initialize_quiz_state

from google.genai import types
from typing import Optional



# Callback to initialize quiz state
# https://google.github.io/adk-docs/callbacks/types-of-callbacks/#before-agent-callback
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Initialize quiz state if not already present"""
    initialize_quiz_state(callback_context.state)
    return None


# Retry configuration for the agent invoking the LLM
retry_config = types.HttpRetryOptions(
    attempts=3,
    initial_delay=1,
    exp_base=5,
    http_status_codes=[429, 500, 503, 504],
)


# The initial agent
root_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
    ),
    name='QuizAgent',
    description='A helpful quiz master with a theoretical knowledge of guitar playing.',
    instruction=quiz_instructions,
    tools=[get_quiz_questions, 
           start_quiz, 
           submit_answer, 
           get_current_question, 
           get_quiz_status, 
           reset_quiz],
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
