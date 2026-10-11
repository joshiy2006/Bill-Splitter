from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from app.deps import check_group_ownership
from app.db import db_client
from app.schemas.expense import ExpenseCreate, ExpenseResponse
from app.services.expense_service import (
    create_expense_service,
    fetch_expenses_indexed,
    suggest_expense_prefixes
)

router = APIRouter(prefix="/groups/{id}/expenses", tags=["Expenses"])

@router.post("", response_model=ExpenseResponse)
def add_expense(id: str, expense: ExpenseCreate, _gid: str = Depends(check_group_ownership)):
    data = expense.model_dump()
    return create_expense_service(id, data)


@router.get("")
def list_expenses(
    id: str,
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    payer: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, alias="from"),
    date_to: Optional[str] = Query(None, alias="to"),
    min_amount: Optional[int] = Query(None, alias="min"),
    max_amount: Optional[int] = Query(None, alias="max"),
    _gid: str = Depends(check_group_ownership)
):
    return fetch_expenses_indexed(
        group_id=id,
        q=q,
        category=category,
        payer=payer,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount
    )


@router.get("/suggest")
def suggest_expense_words(id: str, prefix: str = Query(""), _gid: str = Depends(check_group_ownership)):
    return suggest_expense_prefixes(id, prefix)


@router.delete("/{eid}")
def delete_expense(id: str, eid: str, _gid: str = Depends(check_group_ownership)):
    try:
        db_client.table("expenses").delete().eq("id", eid).execute()
    except Exception:
        pass
    return {"status": "deleted", "id": eid}


@router.patch("/{eid}", response_model=ExpenseResponse)
def update_expense(id: str, eid: str, expense: ExpenseCreate, _gid: str = Depends(check_group_ownership)):
    try:
        db_client.table("expense_splits").delete().eq("expense_id", eid).execute()
        db_client.table("expenses").delete().eq("id", eid).execute()
    except Exception:
        pass
    
    data = expense.model_dump()
    return create_expense_service(id, data)
