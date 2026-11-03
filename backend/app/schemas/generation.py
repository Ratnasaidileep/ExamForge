from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
import datetime

class StructuredGeneratedQuestion(BaseModel):
    question_text: str = Field(description="The full question text clearly stated.")
    question_type: str = Field(description="One of: mcq, short_answer, long_answer")
    options: Optional[List[str]] = Field(default=None, description="4 distinct choices if question_type is mcq, otherwise null")
    correct_answer: Optional[str] = Field(default=None, description="The correct option letter or text for mcq, otherwise null")
    model_answer: Optional[str] = Field(default=None, description="Detailed model answer for descriptive questions")
    rubric: Optional[List[Dict[str, Any]]] = Field(default=None, description="Grading criteria and mark allocation for descriptive questions")
    explanation: Optional[str] = Field(default=None, description="Clear rationale explaining why the answer is correct")
    difficulty: str = Field(default="medium", description="easy, medium, or hard")
    marks: float = Field(default=2.0, description="Marks allocated for this question")
    topic_name: Optional[str] = Field(default=None, description="Topic name from the source text")
    unit_number: Optional[int] = Field(default=None, description="Unit number if mentioned in the document")
    supporting_excerpt: str = Field(description="Direct verbatim sentence or short passage from the source text that justifies this question and answer")
    page_number: Optional[int] = Field(default=None, description="Source page number if clearly identifiable")

class StructuredGenerationBatch(BaseModel):
    questions: List[StructuredGeneratedQuestion]

class GenerationRequest(BaseModel):
    document_id: str
    subject_id: Optional[str] = None
    unit_number: Optional[int] = None
    topic_id: Optional[int] = None
    topic_name: Optional[str] = None
    question_types: List[str] = ["mcq", "short_answer", "long_answer"]
    difficulty: str = "mixed" # easy, medium, hard, mixed
    requested_count: int = 5
    marks_per_question: Optional[float] = None
    custom_instructions: Optional[str] = None
    use_offline_demo: Optional[bool] = False

class GeneratedQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    generation_job_id: str
    document_id: Optional[str] = None
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
    supporting_excerpt: Optional[str] = None
    page_number: Optional[int] = None
    confidence_flag: str
    review_status: str
    approved_question_id: Optional[str] = None
    created_at: datetime.datetime

class GeneratedQuestionUpdate(BaseModel):
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

class GenerationJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    subject_id: Optional[str] = None
    document_id: Optional[str] = None
    prompt_summary: Optional[str] = None
    question_types: List[str] = []
    difficulty: str
    requested_count: int
    marks_per_question: float
    status: str
    error_message: Optional[str] = None
    created_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    generated_questions: List[GeneratedQuestionResponse] = []
