from pydantic import BaseModel, Field
from typing import List, Optional

class ItemAllocationInput(BaseModel):
    id: Optional[str] = None
    description: str
    amount_paise: int = Field(..., gt=0)

class AllocationResponse(BaseModel):
    group_1: List[ItemAllocationInput]
    group_2: List[ItemAllocationInput]
    group_1_total: int
    group_2_total: int
    difference: int
