from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentResponse(BaseModel):
    id: str
    group_id: str
    from_member: str
    to_member: str
    amount_paise: int
    txn_id: Optional[str] = None
    created_at: datetime
