from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import date, datetime

SettlementMethod = Literal['greedy', 'dp']
TxnStatus = Literal['pending', 'paid', 'cancelled']

class SettlementTransactionResponse(BaseModel):
    id: Optional[str] = None
    run_id: Optional[str] = None
    from_member: str
    to_member: str
    amount_paise: int
    due_date: Optional[date] = None
    priority: int = 0
    status: TxnStatus = "pending"
    paid_at: Optional[datetime] = None

class SettlementRunPlan(BaseModel):
    method: SettlementMethod
    member_count: int
    nonzero_count: int
    txn_count: int
    total_moved_paise: int
    runtime_ms: float
    transactions: List[SettlementTransactionResponse]

class SettleCompareResponse(BaseModel):
    compare_id: str
    greedy: SettlementRunPlan
    dp: Optional[SettlementRunPlan] = None
    transactions_saved_by_dp: int
    dp_notice: Optional[str] = None

class SettleAdoptRequest(BaseModel):
    run_id: str

class SettleAdoptResponse(BaseModel):
    status: str
    active_run_id: str
    scheduled_transactions: List[SettlementTransactionResponse]
