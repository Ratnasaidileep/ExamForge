from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
import datetime

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    title: str
    subject_id: Optional[str] = None
    unit_number: Optional[int] = None
    original_filename: str
    file_type: str
    file_size: int
    extraction_status: str
    error_message: Optional[str] = None
    detected_headings: List[Any] = []
    is_demo_seed: bool = False
    created_at: datetime.datetime
    updated_at: datetime.datetime

class DocumentContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    document_id: str
    full_text: str
    page_count: int
    topics_json: List[str] = []

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    subject_id: Optional[str] = None
    unit_number: Optional[int] = None
