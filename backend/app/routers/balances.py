from fastapi import APIRouter, Depends
from typing import Dict, Any
from app.deps import check_group_ownership
from app.services.settlement_service import fetch_group_balances, fetch_debt_graph

router = APIRouter(prefix="/groups/{id}", tags=["Balances & Debt Graph"])

@router.get("/balances")
def get_balances(id: str, _gid: str = Depends(check_group_ownership)):
    balances = fetch_group_balances(id)
    return balances


@router.get("/debt-graph")
def get_debt_graph_route(id: str, _gid: str = Depends(check_group_ownership)):
    return fetch_debt_graph(id)
