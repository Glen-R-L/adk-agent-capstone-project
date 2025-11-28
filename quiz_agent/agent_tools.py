from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import google_search
from google.adk.tools.function_tool import FunctionTool

from google.genai import types

from .function_tools import search_youtube_videos
from .prompts import youtube_instructions, diagram_instructions
from .agent_utils import retry_config


# Agent tool for retrieving an appropriate video from YouTube
youtube_agent = LlmAgent(
    name="YoutubeAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
    ),
    instruction=youtube_instructions,
    tools=[FunctionTool(func=search_youtube_videos)],
)


# Agent tool for linking to a helpful online resource with diagrams
diagram_agent = LlmAgent(
    name="DiagramAgent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config,
    ),
    instruction=diagram_instructions,
    tools=[google_search],
)

