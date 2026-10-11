"""
Priority-Queue Smart Payment Scheduling.

Strategy: MinHeap priority queue ordering transactions by due_date ascending, then amount_paise descending.
Time Complexity: O(t log t) where t is transaction count.
Space Complexity: O(t) for queue storage.
Correctness: Guarantees highest urgency payments (earliest due date, largest amount) receive highest priority (1, 2, ...).
"""

from datetime import date, timedelta
from typing import List, Dict, Any, Optional
from app.algorithms.heap import MinHeap

def schedule_payments(transactions: List[Dict[str, Any]], today: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Schedules settlement transactions by urgency (due_date ascending, amount_paise descending).
    Assigns priority 1, 2, 3, ...
    
    :param transactions: List of transaction dicts (from_member, to_member, amount_paise, due_date).
    :param today: ISO date string 'YYYY-MM-DD' or None (defaults to today's date).
    :return: List of transaction dicts with assigned priority and valid due_date.
    """
    if not transactions:
        return []

    if today:
        ref_date = date.fromisoformat(today)
    else:
        ref_date = date.today()

    default_due = (ref_date + timedelta(days=7)).isoformat()

    heap = MinHeap()

    for idx, txn in enumerate(transactions):
        d_str = txn.get("due_date") or default_due
        amt = int(txn.get("amount_paise", 0))
        # Key: (due_date_str, -amt, idx) for deterministic min-heap sorting
        heap.push((d_str, -amt, idx), txn)

    scheduled = []
    priority = 1

    while len(heap) > 0:
        (d_str, neg_amt, idx), txn = heap.pop()
        txn_copy = dict(txn)
        txn_copy["due_date"] = d_str
        txn_copy["priority"] = priority
        priority += 1
        scheduled.append(txn_copy)

    return scheduled
