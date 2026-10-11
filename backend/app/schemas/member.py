from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MemberCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=60)
    email: Optional[str] = None

class MemberResponse(BaseModel):
    id: str
    group_id: str
    name: str
    email: Optional[str] = None
    created_at: datetime
