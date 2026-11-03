from pydantic import BaseModel, ConfigDict
from typing import Optional
import datetime

class DemoUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    name: str
    role: str
    email: str
    department: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime.datetime

class DemoSwitchRequest(BaseModel):
    user_id: str
