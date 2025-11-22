from google.adk.tools import ToolContext
from typing import Dict, Any

from .quiz_data import questions


# Function for starting the quiz
def start_quiz(tool_context: ToolContext) -> Dict[str, Any]:
    state = tool_context.state
    # Quiz questions loaded into state
    state.setdefault("quiz", questions)
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
    state.setdefault("quiz", questions)
    i = state.get("current_question_index", 0)
    quiz = state.get("quiz", [])
    correct_answer = quiz[i][1]
    is_correct = answer.strip().lower() == correct_answer.strip().lower()
    state["total_answered"] = state.get("total_answered", 0) + 1
    if is_correct:
        state["correct_answers"] = state.get("correct_answers", 0) + 1