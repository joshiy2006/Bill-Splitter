from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.deps import check_group_ownership
from app.schemas.allocate import ItemAllocationInput, AllocationResponse
from app.algorithms.partition import balanced_partition

router = APIRouter(prefix="/groups/{id}/allocate", tags=["Balanced Item Allocation"])

@router.post("", response_model=AllocationResponse)
def allocate_items(id: str, items: List[ItemAllocationInput], _gid: str = Depends(check_group_ownership)):
    item_dicts = [item.model_dump() for item in items]
    res = balanced_partition(item_dicts)
    return res
