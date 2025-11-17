from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search

from google.genai import types


retry_config = types.HttpRetryOptions(
    attempts=3,
    initial_delay=1,
    exp_base=5,
    http_status_codes=[429, 500, 503, 504],
)

root_agent = LlmAgent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
    ),
    name='guitar_tutor',
    description='A helpful tutor with a knowledge of guitar playing.',
    instruction='Help to teach a user about playing guitar.',
    tools=[google_search],
)

runner = InMemoryRunner(agent=root_agent)

# response = runner.run_debug(
#     "How should I learn to play guitar?"
# )
