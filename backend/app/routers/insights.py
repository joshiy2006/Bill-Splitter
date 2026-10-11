from fastapi import APIRouter, Depends, Query
from typing import Dict, Any
from app.deps import check_group_ownership
from app.schemas.insights import InsightsResponse
from app.services.insight_service import fetch_top_insights

router = APIRouter(prefix="/groups/{id}/insights", tags=["Insights & Top-K"])

@router.get("/top", response_model=InsightsResponse)
def get_insights(id: str, k: int = Query(5, ge=1, le=20), _gid: str = Depends(check_group_ownership)):
    return fetch_top_insights(id, k=k)
