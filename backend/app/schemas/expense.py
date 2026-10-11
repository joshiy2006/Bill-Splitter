from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import date, datetime

SplitType = Literal['equal', 'exact', 'percentage', 'shares']

class ParticipantSplitInput(BaseModel):
    member_id: str
    owed_paise: Optional[int] = Field(default=None, ge=0)
    percentage: Optional[float] = Field(default=None, ge=0.0, le=100.0)
    shares: Optional[float] = Field(default=None, ge=0.0)

class ExpenseCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=200)
    category: str = Field(default="general")
    amount_paise: int = Field(..., gt=0)
    paid_by: str
    split_type: SplitType = Field(default="equal")
    expense_date: Optional[date] = None
    participants: List[ParticipantSplitInput]

class ExpenseSplitResponse(BaseModel):
    expense_id: str
    member_id: str
    owed_paise: int
    share_value: Optional[float] = None

class ExpenseResponse(BaseModel):
    id: str
    group_id: str
    description: str
    category: str
    amount_paise: int
    paid_by: str
    split_type: SplitType
    expense_date: date
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    splits: Optional[List[ExpenseSplitResponse]] = None
