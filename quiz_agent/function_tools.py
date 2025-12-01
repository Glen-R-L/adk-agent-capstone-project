import os
from googleapiclient.discovery import build
from typing import Dict, List, Any

from google.adk.tools.tool_context import ToolContext

from .quiz_data import quiz_questions
from .agent_utils import YouTubeVideo, YouTubeSearchResults



# Function for getting all quiz questions
def get_quiz_questions() -> Dict[str, Any]:
    """
    Get all quiz questions for the Guitar Playing Theory quiz.

    Returns:
        Dictionary containing:
        - total_questions: Total number of questions in the quiz
        - questions: List of all question texts
    """
    return {
        "status": "success",
        "total_questions": len(quiz_questions),
        "questions": [q[0] for q in quiz_questions],
    }


# Function for starting the quiz
def start_quiz(tool_context: ToolContext) -> Dict[str, Any]:
    state = tool_context.state
    # Quiz questions loaded into state
    state.setdefault("quiz", quiz_questions)
    # Initialize quiz state
    state["quiz_started"] = True
    state["current_question_index"] = 0
    state["correct_answers"] = 0
    state["total_answered"] = 0
    state["score_percentage"] = 0
    quiz = state.get("quiz", [])
    if quiz:
        first_q = quiz[0][0] if isinstance(quiz[0], (list, tuple)) and len(quiz[0]) > 0 else quiz[0]
        return {
            "status": "started",
            "first_question": first_q,
            "question_number": 1,
            "total_questions": len(quiz),
        }
    return {"status": "error", "error_message": "No questions available"}


# Function for submitting an answer
def submit_answer(tool_context: ToolContext, answer: str) -> Dict[str, Any]:
    state = tool_context.state
    # Quiz questions loaded into state
    state.setdefault("quiz", quiz_questions)
    i = state.get("current_question_index", 0)
    total_answered = state.get("total_answered", 0)

    # Prevent re-answering the same question
    if i < total_answered:
        return {
            "status": "error",
            "message": "This question has already been answered. Please wait for the next question.",
        }
    quiz = state.get("quiz")
    if not quiz:
        return {
            "status": "error",
            "message": "Quiz data is missing from the state. Please start the quiz.",
        }
    correct_answer = quiz[i][1]
    is_correct = answer.strip().lower() == correct_answer.strip().lower()
    state["total_answered"] = state.get("total_answered", 0) + 1
    if is_correct:
        state["correct_answers"] = state.get("correct_answers", 0) + 1
    
    # Update score percentage
    total_answered = state.get("total_answered", 0)
    if total_answered > 0:
        state["score_percentage"] = (state.get("correct_answers", 0) / total_answered) * 100

    # Move to the next question
    state["current_question_index"] = i + 1

    # Check if there is a next question and return it
    next_i = state.get("current_question_index", 0)
    if next_i < len(quiz):
        return {
            "status": "success",
            "is_correct": is_correct,
            "next_question": quiz[next_i][0],
            "next_question_number": next_i + 1,
            "total_questions": len(quiz),
        }

    # If the quiz is over
    return {
        "status": "quiz_completed",
        "is_correct": is_correct,
    }


def get_current_question(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get the current question in the quiz.

    Returns:
        Dictionary containing:
        - status: 'success' or 'error'
        - question: Current question text
        - question_number: Current question number
        - total_questions: Total number of questions
    """
    state = tool_context.state

    if not state.get("quiz_started", False):
        return {
            "status": "error",
            "error_message": "Quiz not started. Please start the quiz first.",
        }

    i = state.get("current_question_index", 0)
    quiz = state.get("quiz", quiz_questions)
    if i < len(quiz):
        return {
            "status": "success",
            "question": quiz[i][0],
            "question_number": i + 1,
            "total_questions": len(quiz),
        }
    return {
        "status": "quiz_completed",
        "message": "The quiz is complete!",
    }


def get_quiz_status(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Get the current status of the quiz including score and progress.

    Returns:
        Dictionary containing:
        - quiz_started: Whether quiz has been started
        - current_question_index: Index of current question (0-based)
        - questions_answered: Number of questions answered
        - correct_answers: Number of correct answers
        - score_percentage: Current percentage score
        - questions_remaining: Number of questions left
        - total_questions: Total number of questions
    """
    state = tool_context.state

    return {
        "status": "success",
        "quiz_started": state.get("quiz_started", False),
        "current_question_index": state.get("current_question_index", 0),
        "questions_answered": state.get("total_answered", 0),
        "correct_answers": state.get("correct_answers", 0),
        "score_percentage": state.get("score_percentage", 0),
        "questions_remaining": len(quiz_questions) - state.get("current_question_index", 0),
        "total_questions": len(quiz_questions),
    }


def reset_quiz(tool_context: ToolContext) -> Dict[str, Any]:
    """
    Reset the quiz to start over from the beginning.

    Returns:
        Dictionary containing:
        - status: 'success'
        - message: Confirmation message
    """
    state = tool_context.state

    state["quiz_started"] = False
    state["current_question_index"] = 0
    state["correct_answers"] = 0
    state["total_answered"] = 0
    state["score_percentage"] = 0

    return {
        "status": "success",
        "message": "Quiz has been reset. You can start again whenever you're ready.",
    }


# Custom Function tool for fetching and correctly recieving youtube URLs - for the youtube_agent
def search_youtube_videos(query: str, max_results: int = 3) -> YouTubeSearchResults:
    """
    Searches YouTube for videos based on a query and returns a structured list of results.
    
    ARGS:
        query: Provided by the root agent as {session.genre_choice}
        max_results (optional): Maximum number of videos returned in the YouTubeSearchResults list - set to 3 by default

    RETURNS:
        List of videos (YouTubeVideo objects) as a YouTubeSearchResults object
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY environment variable not set.")

    youtube = build('youtube', 'v3', developerKey=api_key)

    request = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        maxResults=max_results
    )

    response = request.execute()

    videos = []
    for item in response.get('items', []):
        video_id = item['id']['videoId']
        # ... fetch other details ...
        url = f"https://www.youtube.com/watch?v={video_id}"

        videos.append(YouTubeVideo(
            title=item['snippet']['title'],
            video_id=video_id,
            url=url,
            channel_title=item['snippet']['channelTitle']
        ))

    return YouTubeSearchResults(results=videos)
