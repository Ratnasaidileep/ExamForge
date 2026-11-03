from pydantic import BaseModel, ConfigDict
from typing import Optional, List
import datetime

class TopicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    subject_id: str
    unit_number: int
    unit_name: str
    topic_name: str
    description: Optional[str] = None

class SubjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    code: str
    name: str
    description: Optional[str] = None
    topics: List[TopicResponse] = []
    created_at: datetime.datetime
