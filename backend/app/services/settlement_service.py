import uuid
from typing import Dict, List, Any, Optional
from datetime import date, datetime
from fastapi import HTTPException
from app.db import db_client
from app.algorithms.balances import net_balances, pairwise_debts
from app.algorithms.graph import DebtGraph, cancel_cycles
from app.algorithms.greedy import settle_greedy
from app.algorithms.dp_optimal import settle_dp, DpSizeError
from app.algorithms.scheduler import schedule_payments

def fetch_group_balances(group_id: str) -> Dict[str, int]:
    """
    Computes exact net balances for all group members from DB expenses, splits, and payments.
    """
    res_mem = db_client.table("members").select("id").eq("group_id", group_id).execute()
    members = [m["id"] for m in (res_mem.data or []) if isinstance(m, dict)]
    if not members:
        return {}

    res_exp = db_client.table("expenses").select("id, paid_by, amount_paise").eq("group_id", group_id).execute()
    expenses = [e for e in (res_exp.data or []) if isinstance(e, dict)]

    exp_ids = [e["id"] for e in expenses]
    splits = []
    if exp_ids:
        res_spl = db_client.table("expense_splits").select("expense_id, member_id, owed_paise").in_("expense_id", exp_ids).execute()
        splits = [s for s in (res_spl.data or []) if isinstance(s, dict)]

    res_pay = db_client.table("payments").select("from_member, to_member, amount_paise").eq("group_id", group_id).execute()
    payments = [p for p in (res_pay.data or []) if isinstance(p, dict)]

    return net_balances(members, expenses, splits, payments)


def fetch_debt_graph(group_id: str) -> Dict[str, Any]:
    """
    Computes raw debt graph and applies DFS cycle cancellation.
    """
    res_exp = db_client.table("expenses").select("id, paid_by, amount_paise").eq("group_id", group_id).execute()
    expenses = [e for e in (res_exp.data or []) if isinstance(e, dict)]

    exp_ids = [e["id"] for e in expenses]
    splits = []
    if exp_ids:
        res_spl = db_client.table("expense_splits").select("expense_id, member_id, owed_paise").in_("expense_id", exp_ids).execute()
        splits = [s for s in (res_spl.data or []) if isinstance(s, dict)]

    res_pay = db_client.table("payments").select("from_member, to_member, amount_paise").eq("group_id", group_id).execute()
    payments = [p for p in (res_pay.data or []) if isinstance(p, dict)]

    raw_debts = pairwise_debts(expenses, splits, payments)

    raw_graph = DebtGraph()
    for (u, v), w in raw_debts.items():
        raw_graph.add_edge(u, v, w)

    raw_edge_list = raw_graph.to_edge_list()

    cancel_graph = DebtGraph()
    for (u, v), w in raw_debts.items():
        cancel_graph.add_edge(u, v, w)

    simplified_graph, cancelled_cycles = cancel_cycles(cancel_graph)
    simplified_edge_list = simplified_graph.to_edge_list()

    return {
        "raw": raw_edge_list,
        "simplified": simplified_edge_list,
        "cancelled_cycles": cancelled_cycles
    }


def compare_settlement_plans(group_id: str) -> Dict[str, Any]:
    """
    Runs Greedy and Bitmask DP on current balances, saves both runs sharing compare_id in DB,
    and returns comparison metrics.
    """
    balances = fetch_group_balances(group_id)
    nonzero_count = sum(1 for v in balances.values() if v != 0)
    member_count = len(balances)

    compare_id = str(uuid.uuid4())

    greedy_res = settle_greedy(balances)
    greedy_run_id = str(uuid.uuid4())
    greedy_run_record = {
        "id": greedy_run_id,
        "group_id": group_id,
        "compare_id": compare_id,
        "method": "greedy",
        "is_active": False,
        "member_count": member_count,
        "nonzero_count": nonzero_count,
        "txn_count": greedy_res["txn_count"],
        "total_moved_paise": greedy_res["total_moved_paise"],
        "runtime_ms": greedy_res["runtime_ms"],
        "balances": balances
    }
    db_client.table("settlement_runs").insert(greedy_run_record).execute()

    greedy_plan = {
        "id": greedy_run_id,
        "method": "greedy",
        "member_count": member_count,
        "nonzero_count": nonzero_count,
        "txn_count": greedy_res["txn_count"],
        "total_moved_paise": greedy_res["total_moved_paise"],
        "runtime_ms": greedy_res["runtime_ms"],
        "transactions": greedy_res["transactions"]
    }

    dp_plan = None
    dp_notice = None
    txns_saved = 0

    if nonzero_count > 18:
        dp_notice = f"Optimal Bitmask DP skipped because non-zero members count ({nonzero_count}) > 18."
    else:
        try:
            dp_res = settle_dp(balances)
            dp_run_id = str(uuid.uuid4())
            dp_run_record = {
                "id": dp_run_id,
                "group_id": group_id,
                "compare_id": compare_id,
                "method": "dp",
                "is_active": False,
                "member_count": member_count,
                "nonzero_count": nonzero_count,
                "txn_count": dp_res["txn_count"],
                "total_moved_paise": dp_res["total_moved_paise"],
                "runtime_ms": dp_res["runtime_ms"],
                "balances": balances
            }
            db_client.table("settlement_runs").insert(dp_run_record).execute()

            dp_plan = {
                "id": dp_run_id,
                "method": "dp",
                "member_count": member_count,
                "nonzero_count": nonzero_count,
                "txn_count": dp_res["txn_count"],
                "total_moved_paise": dp_res["total_moved_paise"],
                "runtime_ms": dp_res["runtime_ms"],
                "transactions": dp_res["transactions"]
            }
            txns_saved = greedy_res["txn_count"] - dp_res["txn_count"]
        except DpSizeError as e:
            dp_notice = str(e)

    return {
        "compare_id": compare_id,
        "greedy": greedy_plan,
        "dp": dp_plan,
        "transactions_saved_by_dp": max(0, txns_saved),
        "dp_notice": dp_notice
    }


def adopt_settlement_plan(group_id: str, run_id: str) -> Dict[str, Any]:
    """
    Marks selected run_id active (deactivating old active run), runs priority-queue payment
    scheduler, and saves settlement transactions in DB.
    """
    res_run = db_client.table("settlement_runs").select("*").eq("id", run_id).single().execute()
    if not res_run or not res_run.data:
        raise HTTPException(status_code=404, detail="Settlement run not found")

    run_data = res_run.data
    if isinstance(run_data, list):
        if len(run_data) == 0:
            raise HTTPException(status_code=404, detail="Settlement run not found")
        run_data = run_data[0]

    balances = run_data.get("balances", {})
    method = run_data.get("method", "greedy")

    if method == "greedy":
        res_alg = settle_greedy(balances)
    else:
        res_alg = settle_dp(balances)

    raw_txns = res_alg["transactions"]
    scheduled = schedule_payments(raw_txns, today=date.today().isoformat())

    # Deactivate all runs for group, then activate chosen run
    db_client.table("settlement_runs").update({"is_active": False}).eq("group_id", group_id).execute()
    db_client.table("settlement_runs").update({"is_active": True}).eq("id", run_id).execute()
    db_client.table("settlement_transactions").delete().eq("run_id", run_id).execute()

    txn_records = []
    for st in scheduled:
        rec = {
            "id": str(uuid.uuid4()),
            "run_id": run_id,
            "from_member": st["from_member"],
            "to_member": st["to_member"],
            "amount_paise": st["amount_paise"],
            "due_date": st["due_date"],
            "priority": st["priority"],
            "status": "pending"
        }
        txn_records.append(rec)

    if txn_records:
        db_client.table("settlement_transactions").insert(txn_records).execute()

    return {
        "status": "adopted",
        "active_run_id": run_id,
        "scheduled_transactions": txn_records
    }


def fetch_payment_queue(group_id: str) -> List[Dict[str, Any]]:
    """
    Returns pending settlement transactions in priority order for the active settlement run.
    """
    res_run = db_client.table("settlement_runs").select("id").eq("group_id", group_id).eq("is_active", True).execute()
    active_runs = res_run.data or []
    if not active_runs:
        return []

    active_item = active_runs[-1] if isinstance(active_runs, list) else active_runs
    active_run_id = active_item.get("id") if isinstance(active_item, dict) else None

    if not active_run_id:
        return []

    res_txns = db_client.table("settlement_transactions").select("*").eq("run_id", active_run_id).order("priority", desc=False).execute()
    return res_txns.data or []


def mark_payment_paid(group_id: str, txn_id: str) -> Dict[str, Any]:
    """
    Marks settlement transaction paid and creates corresponding payments table row.
    """
    res_txn = db_client.table("settlement_transactions").select("*").eq("id", txn_id).single().execute()
    if not res_txn or not res_txn.data:
        raise HTTPException(status_code=404, detail="Settlement transaction not found")

    txn = res_txn.data
    if isinstance(txn, list):
        if len(txn) == 0:
            raise HTTPException(status_code=404, detail="Settlement transaction not found")
        txn = txn[0]

    now_iso = datetime.now().isoformat()

    db_client.table("settlement_transactions").update({
        "status": "paid",
        "paid_at": now_iso
    }).eq("id", txn_id).execute()

    pay_record = {
        "id": str(uuid.uuid4()),
        "group_id": group_id,
        "from_member": txn["from_member"],
        "to_member": txn["to_member"],
        "amount_paise": txn["amount_paise"],
        "txn_id": txn_id,
        "created_at": now_iso
    }
    db_client.table("payments").insert(pay_record).execute()

    return pay_record
