from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
import datetime

class GradingQueueItemResponse(BaseModel):
    attempt_id: str
    student_id: str
    student_name: str
    title: str
    submitted_at: datetime.datetime
    pending_count: int
    graded_count: int
    total_descriptive: int
    objective_score: Optional[float] = None
    total_possible_marks: float
    status: str

class DescriptiveResponseToGrade(BaseModel):
    response_id: str
    question_revision_id: str
    question_text: str
    question_type: str
    marks_allocated: float
    submitted_answer: Optional[str] = None
    model_answer: Optional[str] = None
    rubric_json: Optional[List[Dict[str, Any]]] = None
    marks_awarded: Optional[float] = None
    grading_status: str # 'pending', 'manually_graded'
    faculty_feedback: Optional[str] = None
    graded_at: Optional[datetime.datetime] = None

class GradingAttemptDetailResponse(BaseModel):
    attempt_id: str
    student_id: str
    student_name: str
    student_email: str
    title: str
    status: str
    submitted_at: datetime.datetime
    objective_score: Optional[float] = None
    provisional_score: Optional[float] = None
    final_score: Optional[float] = None
    total_possible_marks: float
    responses_to_grade: List[DescriptiveResponseToGrade] = []
    can_finalize: bool = False

class GradeResponseRequest(BaseModel):
    marks_awarded: float = Field(ge=0.0, description="Marks awarded must be non-negative")
    faculty_feedback: Optional[str] = None

class FinalizeGradingRequest(BaseModel):
    notes: Optional[str] = None
