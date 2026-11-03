from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
import datetime

class AttemptCreate(BaseModel):
    paper_id: Optional[str] = None
    question_set_id: Optional[str] = None
    mode: str = "assessment" # 'assessment', 'practice', 'mock'

class ActiveAttemptQuestionResponse(BaseModel):
    question_revision_id: str
    order_index: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    marks_allocated: float
    difficulty: Optional[str] = None
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None
    # STRICT SECURITY: No correct_answer, model_answer, explanation, rubric!

class SavedResponseItem(BaseModel):
    question_revision_id: str
    submitted_answer: Optional[str] = None
    is_marked_for_review: bool = False

class ActiveAttemptResponse(BaseModel):
    id: str
    student_id: str
    paper_id: Optional[str] = None
    question_set_id: Optional[str] = None
    title: str
    subject_id: Optional[str] = None
    mode: str
    status: str
    started_at: datetime.datetime
    deadline_at: Optional[datetime.datetime] = None
    remaining_seconds: Optional[int] = None
    total_questions: int
    total_possible_marks: float
    questions: List[ActiveAttemptQuestionResponse]
    saved_responses: Dict[str, SavedResponseItem] = {}

class ResponseSaveRequest(BaseModel):
    submitted_answer: Optional[str] = None
    is_marked_for_review: Optional[bool] = False

class AttemptSubmissionResponse(BaseModel):
    attempt_id: str
    status: str
    submitted_at: datetime.datetime
    objective_score: Optional[float] = None
    provisional_score: Optional[float] = None
    final_score: Optional[float] = None
    total_possible_marks: float
    requires_manual_grading: bool
    pending_descriptive_count: int
    message: str

class QuestionReviewItem(BaseModel):
    question_revision_id: str
    order_index: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    submitted_answer: Optional[str] = None
    correct_answer: Optional[str] = None # Released only in results
    model_answer: Optional[str] = None   # Released only in results
    rubric_json: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    marks_allocated: float
    marks_awarded: Optional[float] = None # null if pending grading!
    grading_status: str # 'pending', 'auto_graded', 'manually_graded'
    is_correct: Optional[bool] = None
    faculty_feedback: Optional[str] = None
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None

class AttemptResultResponse(BaseModel):
    id: str
    student_id: str
    title: str
    mode: str
    status: str # 'submitted', 'awaiting_grading', 'partially_graded', 'graded'
    started_at: datetime.datetime
    submitted_at: Optional[datetime.datetime] = None
    total_possible_marks: float
    objective_score: Optional[float] = None
    provisional_score: Optional[float] = None # objective score + already graded
    final_score: Optional[float] = None      # Only non-null when fully graded!
    is_fully_graded: bool
    correct_count: int = 0
    incorrect_count: int = 0
    pending_grading_count: int = 0
    topic_performance: List[Dict[str, Any]] = []
    questions: List[QuestionReviewItem] = []
