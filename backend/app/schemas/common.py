from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List, Dict
import datetime

class APIResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    total_pages: int
