from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class TopSpender(BaseModel):
    member_id: str
    member_name: str
    total_spent_paise: int

class TopExpense(BaseModel):
    id: str
    description: str
    amount_paise: int
    category: str
    paid_by: str
    paid_by_name: str
    expense_date: str

class InsightsResponse(BaseModel):
    top_spenders: List[TopSpender]
    top_expenses: List[TopExpense]
    spend_by_category: Dict[str, int]
