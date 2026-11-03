from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
import datetime
from app.schemas.question import QuestionRevisionResponse

class BlueprintRule(BaseModel):
    target_marks: float = 50.0
    duration_minutes: int = 60
    difficulty_target: Optional[Dict[str, float]] = None # {"easy": 30, "medium": 50, "hard": 20} (percentages or counts)
    type_target: Optional[Dict[str, int]] = None # {"mcq": 10, "short_answer": 4, "long_answer": 2}
    required_units: Optional[List[int]] = None # [1, 2, 3, 4]
    required_topics: Optional[List[str]] = None

class ValidationResult(BaseModel):
    is_valid: bool
    can_publish: bool
    total_marks_expected: float
    total_marks_actual: float
    questions_count: int
    difficulty_breakdown: Dict[str, int] = {}
    type_breakdown: Dict[str, int] = {}
    topic_breakdown: Dict[str, int] = {}
    unit_breakdown: Dict[str, int] = {}
    warnings: List[str] = []
    errors: List[str] = []

class PaperItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    paper_id: str
    section_id: Optional[str] = None
    question_revision_id: str
    item_order: int
    marks: float
    revision: Optional[QuestionRevisionResponse] = None

class PaperSectionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    paper_id: str
    name: str
    description: Optional[str] = None
    section_order: int
    total_marks: float
    instructions: Optional[str] = None
    items: List[PaperItemResponse] = []

class PaperResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    subject_id: Optional[str] = None
    status: str # 'draft', 'practice', 'published', 'archived'
    duration_minutes: int
    total_marks: float
    instructions: Optional[str] = None
    blueprint_json: Optional[Dict[str, Any]] = None
    validation_results_json: Optional[Dict[str, Any]] = None
    warnings_acknowledged: bool = False
    window_start: Optional[datetime.datetime] = None
    window_end: Optional[datetime.datetime] = None
    is_demo_seed: bool = False
    question_count: Optional[int] = None
    published_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

class PaperDetailResponse(PaperResponse):
    sections: List[PaperSectionResponse] = []
    items: List[PaperItemResponse] = []

class PaperCreate(BaseModel):
    title: str
    subject_id: Optional[str] = "ITS-401"
    duration_minutes: int = 60
    total_marks: float = 50.0
    instructions: Optional[str] = None
    blueprint_json: Optional[Dict[str, Any]] = None
    window_start: Optional[datetime.datetime] = None
    window_end: Optional[datetime.datetime] = None

class PaperUpdate(BaseModel):
    title: Optional[str] = None
    subject_id: Optional[str] = None
    duration_minutes: Optional[int] = None
    total_marks: Optional[float] = None
    instructions: Optional[str] = None
    blueprint_json: Optional[Dict[str, Any]] = None
    warnings_acknowledged: Optional[bool] = None
    window_start: Optional[datetime.datetime] = None
    window_end: Optional[datetime.datetime] = None
    sections: Optional[List[Dict[str, Any]]] = None # Full layout update

class PaperAssembleRequest(BaseModel):
    blueprint: BlueprintRule
    use_approved_only: bool = True
