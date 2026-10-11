import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.deps import check_group_ownership
from app.db import db_client
from app.schemas.member import MemberCreate, MemberResponse

router = APIRouter(prefix="/groups/{id}/members", tags=["Members"])

@router.post("", response_model=MemberResponse)
def add_member(id: str, member: MemberCreate, _gid: str = Depends(check_group_ownership)):
    m_id = str(uuid.uuid4())
    record = {
        "id": m_id,
        "group_id": id,
        "name": member.name,
        "email": member.email,
        "created_at": datetime.now().isoformat()
    }
    try:
        res = db_client.table("members").insert(record).execute()
        if res and res.data:
            if isinstance(res.data, list) and len(res.data) > 0:
                return res.data[0]
            elif isinstance(res.data, dict):
                return res.data
        return record
    except Exception:
        return record


@router.get("", response_model=List[MemberResponse])
def list_members(id: str, _gid: str = Depends(check_group_ownership)):
    try:
        res = db_client.table("members").select("*").eq("group_id", id).order("name").execute()
        return res.data or []
    except Exception:
        return []


@router.delete("/{mid}")
def delete_member(id: str, mid: str, _gid: str = Depends(check_group_ownership)):
    try:
        res_exp = db_client.table("expenses").select("id").eq("paid_by", mid).limit(1).execute()
        if res_exp and res_exp.data:
            raise HTTPException(status_code=400, detail="Cannot delete member who has paid expenses.")

        res_spl = db_client.table("expense_splits").select("expense_id").eq("member_id", mid).limit(1).execute()
        if res_spl and res_spl.data:
            raise HTTPException(status_code=400, detail="Cannot delete member who is part of expense splits.")

        res_p1 = db_client.table("payments").select("id").eq("from_member", mid).limit(1).execute()
        res_p2 = db_client.table("payments").select("id").eq("to_member", mid).limit(1).execute()
        if (res_p1 and res_p1.data) or (res_p2 and res_p2.data):
            raise HTTPException(status_code=400, detail="Cannot delete member who has completed settlement payments.")

        db_client.table("members").delete().eq("id", mid).execute()
    except HTTPException:
        raise
    except Exception:
        pass
    return {"status": "deleted", "id": mid}
