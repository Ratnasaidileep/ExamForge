from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
import datetime

class QuestionRevisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    question_id: str
    revision_number: int
    question_text: str
    question_type: str
    options_json: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    model_answer: Optional[str] = None
    rubric_json: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    difficulty: str
    marks: float
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None
    source_document_id: Optional[str] = None
    source_document_title: Optional[str] = None
    supporting_excerpt: Optional[str] = None
    page_number: Optional[int] = None
    verified_grounding: bool = True
    approved_by: Optional[str] = None
    approved_at: Optional[datetime.datetime] = None
    is_current: bool = True
    created_at: datetime.datetime

class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    subject_id: Optional[str] = None
    current_revision_id: Optional[str] = None
    status: str
    is_active: bool
    is_demo_seed: bool = False
    current_revision: Optional[QuestionRevisionResponse] = None
    revisions: List[QuestionRevisionResponse] = []
    created_at: datetime.datetime
    updated_at: datetime.datetime

class QuestionCreate(BaseModel):
    subject_id: Optional[str] = None
    question_text: str
    question_type: str
    options_json: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    model_answer: Optional[str] = None
    rubric_json: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    difficulty: str = "medium"
    marks: float = 2.0
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None
    source_document_id: Optional[str] = None
    source_document_title: Optional[str] = None
    supporting_excerpt: Optional[str] = None
    page_number: Optional[int] = None
    status: str = "approved"

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    options_json: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    model_answer: Optional[str] = None
    rubric_json: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    marks: Optional[float] = None
    topic_name: Optional[str] = None
    unit_number: Optional[int] = None
    supporting_excerpt: Optional[str] = None
    requires_reapproval: bool = True

class QuestionApproveRequest(BaseModel):
    notes: Optional[str] = None
