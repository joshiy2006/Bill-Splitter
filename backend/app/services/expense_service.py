import uuid
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from fastapi import HTTPException
from app.db import db_client
from app.algorithms.splits import resolve_split
from app.algorithms.search import ExpenseIndex, filter_expenses

def create_expense_service(group_id: str, expense_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolves splits with resolve_split and inserts expense & splits into DB.
    """
    amount_paise = int(expense_data["amount_paise"])
    split_type = expense_data["split_type"]
    paid_by = expense_data["paid_by"]
    participants = expense_data["participants"]
    description = expense_data["description"]
    category = expense_data.get("category", "general")
    expense_date = expense_data.get("expense_date") or date.today().isoformat()
    now_iso = datetime.now().isoformat()

    # 1. Resolve splits using pure algorithm
    try:
        resolved_splits = resolve_split(amount_paise, split_type, participants)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 2. Generate UUIDs
    exp_id = str(uuid.uuid4())

    # 3. Insert expense record
    exp_record = {
        "id": exp_id,
        "group_id": group_id,
        "description": description,
        "category": category,
        "amount_paise": amount_paise,
        "paid_by": paid_by,
        "split_type": split_type,
        "expense_date": expense_date,
        "created_at": now_iso,
        "updated_at": now_iso
    }

    try:
        db_client.table("expenses").insert(exp_record).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert expense: {str(e)}")

    # 4. Insert splits
    splits_records = [
        {
            "expense_id": exp_id,
            "member_id": s["member_id"],
            "owed_paise": s["owed_paise"],
            "share_value": s.get("share_value")
        }
        for s in resolved_splits
    ]

    try:
        db_client.table("expense_splits").insert(splits_records).execute()
    except Exception as e:
        db_client.table("expenses").delete().eq("id", exp_id).execute()
        raise HTTPException(status_code=400, detail=f"Failed to insert expense splits: {str(e)}")

    exp_record["splits"] = splits_records
    return exp_record


def fetch_expenses_indexed(
    group_id: str,
    q: Optional[str] = None,
    category: Optional[str] = None,
    payer: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetches all group expenses, builds Trie/Inverted index, and returns filtered list.
    """
    res_exp = db_client.table("expenses").select("*").eq("group_id", group_id).execute()
    expenses = res_exp.data or []

    res_mem = db_client.table("members").select("id, name").eq("group_id", group_id).execute()
    members = res_mem.data or []
    member_map = {m["id"]: m["name"] for m in members}

    if not expenses:
        return []

    res_splits = db_client.table("expense_splits").select("*").in_("expense_id", [e["id"] for e in expenses]).execute()
    splits_by_exp: Dict[str, List[Dict[str, Any]]] = {}
    for s in (res_splits.data or []):
        exp_id = s["expense_id"]
        if exp_id not in splits_by_exp:
            splits_by_exp[exp_id] = []
        splits_by_exp[exp_id].append(s)

    exp_dict = {e["id"]: dict(e, splits=splits_by_exp.get(e["id"], [])) for e in expenses}

    index = ExpenseIndex()
    index.build(expenses, member_map)

    filtered = filter_expenses(
        index,
        exp_dict,
        q=q,
        category=category,
        payer=payer,
        date_from=date_from,
        date_to=date_to,
        min_amount=min_amount,
        max_amount=max_amount
    )
    return filtered


def suggest_expense_prefixes(group_id: str, prefix: str) -> List[str]:
    """
    Autocomplete prefix search using Trie.
    """
    res_exp = db_client.table("expenses").select("description, category").eq("group_id", group_id).execute()
    expenses = res_exp.data or []
    index = ExpenseIndex()
    index.build(expenses)
    return index.trie.autocomplete(prefix, limit=6)
