from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=80)
    currency: str = Field(default="INR", max_length=3)

class GroupResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    currency: str
    created_at: datetime
