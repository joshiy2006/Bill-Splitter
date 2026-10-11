from typing import Dict, List, Any
from app.db import db_client
from app.algorithms.heap import top_k

def fetch_top_insights(group_id: str, k: int = 5) -> Dict[str, Any]:
    """
    Computes top-k spenders (using MinHeap top_k), top-k expenses, and spend by category.
    """
    res_exp = db_client.table("expenses").select("*").eq("group_id", group_id).execute()
    expenses = res_exp.data or []

    res_mem = db_client.table("members").select("id, name").eq("group_id", group_id).execute()
    members = res_mem.data or []
    member_names = {m["id"]: m["name"] for m in members}

    if not expenses:
        return {
            "top_spenders": [],
            "top_expenses": [],
            "spend_by_category": {}
        }

    # 1. Total spent by member
    spender_totals: Dict[str, int] = {}
    category_totals: Dict[str, int] = {}

    for exp in expenses:
        payer = str(exp["paid_by"])
        amt = int(exp["amount_paise"])
        cat = str(exp.get("category", "general"))

        spender_totals[payer] = spender_totals.get(payer, 0) + amt
        category_totals[cat] = category_totals.get(cat, 0) + amt

    # Top-k spenders using MinHeap top_k algorithm
    spender_items = [{"member_id": m_id, "member_name": member_names.get(m_id, m_id), "total_spent_paise": total}
                     for m_id, total in spender_totals.items()]
    top_spenders = top_k(spender_items, k, key=lambda x: x["total_spent_paise"])

    # Top-k expenses using MinHeap top_k algorithm
    formatted_exp = [
        {
            "id": exp["id"],
            "description": exp["description"],
            "amount_paise": int(exp["amount_paise"]),
            "category": exp.get("category", "general"),
            "paid_by": exp["paid_by"],
            "paid_by_name": member_names.get(exp["paid_by"], exp["paid_by"]),
            "expense_date": exp.get("expense_date", "")
        }
        for exp in expenses
    ]
    top_expenses = top_k(formatted_exp, k, key=lambda x: x["amount_paise"])

    return {
        "top_spenders": top_spenders,
        "top_expenses": top_expenses,
        "spend_by_category": category_totals
    }
