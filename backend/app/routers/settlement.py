from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
from app.deps import check_group_ownership
from app.schemas.settlement import SettleAdoptRequest, SettleAdoptResponse
from app.services.settlement_service import compare_settlement_plans, adopt_settlement_plan

router = APIRouter(prefix="/groups/{id}/settle", tags=["Settlement"])

@router.post("/compare")
def compare_settlements(id: str, _gid: str = Depends(check_group_ownership)):
    return compare_settlement_plans(id)


@router.post("/adopt", response_model=SettleAdoptResponse)
def adopt_settlement(id: str, req: SettleAdoptRequest, _gid: str = Depends(check_group_ownership)):
    return adopt_settlement_plan(id, req.run_id)
