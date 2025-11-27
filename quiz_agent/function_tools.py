from google.adk.tools.tool_context import ToolContext
from typing import Dict, Any

from .quiz_data import quiz_questions



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
    quiz = state.get("quiz", [])
    correct_answer = quiz[i][1]
    is_correct = answer.strip().lower() == correct_answer.strip().lower()
    state["total_answered"] = state.get("total_answered", 0) + 1
    if is_correct:
        state["correct_answers"] = state.get("correct_answers", 0) + 1


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
    if i < len(quiz_questions):
        return {
            "status": "success",
            "question": quiz_questions[i][0],
            "question_number": i + 1,
            "total_questions": len(quiz_questions),
        }
    return {
        "status": "error",
        "error_message": "No current question - quiz may be complete",
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