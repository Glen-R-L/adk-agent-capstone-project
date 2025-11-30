from typing import Dict, List, Any
from google.genai import types

from pydantic import BaseModel, Field


# From the callback in agent.py - to initialize quiz state
def initialize_quiz_state(state: Dict[str, Any], with_memory: bool = False):
    """
    Initializes the quiz state in the provided state dictionary.

    Args:
        state: The state dictionary to initialize.
        with_memory: Whether to initialize memory-related state.
    """
    if "quiz_initialized" not in state:
        state["quiz_initialized"] = True
        state["current_question_index"] = 0
        state["correct_answers"] = 0
        state["total_answered"] = 0
        state["score_percentage"] = 0
        state["quiz_started"] = False
        state["review_topic"] = ''
        state["genre_choice"] = ''
        if with_memory:
            state["user:name"] = ''
        print("[Callback] Initialized quiz state")


# Retry configuration for each agent invoking it's LLM
retry_config = types.HttpRetryOptions(
    attempts=3,
    initial_delay=1,
    exp_base=5,
    http_status_codes=[429, 500, 503, 504],
)


# Pydantic data models for the youtube_agent's search_youtube_videos tool
class YouTubeVideo(BaseModel):
    """Structured data for a single YouTube video."""
    title: str = Field(description="The title of the YouTube video.")
    video_id: str = Field(description="The unique YouTube video ID (e.g., 'dQw4w9WgXcQ').")
    url: str = Field(description="The full, valid URL for the video.")
    channel_title: str = Field(description="The name of the channel that published the video.")

class YouTubeSearchResults(BaseModel):
    """A list of up to three YouTube video search results."""
    results: List[YouTubeVideo]