from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.deps import check_group_ownership
from app.schemas.payment import PaymentResponse
from app.services.settlement_service import fetch_payment_queue, mark_payment_paid

router = APIRouter(prefix="/groups/{id}/payments", tags=["Payments Queue"])

@router.get("/queue")
def get_payment_queue_route(id: str, _gid: str = Depends(check_group_ownership)):
    return fetch_payment_queue(id)


@router.post("/{txn_id}/pay", response_model=PaymentResponse)
def pay_transaction_route(id: str, txn_id: str, _gid: str = Depends(check_group_ownership)):
    return mark_payment_paid(id, txn_id)
