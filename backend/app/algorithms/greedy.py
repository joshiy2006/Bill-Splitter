"""
Greedy Debt Settlement using two custom MaxHeaps (Creditors and Debtors).

Strategy: Two max-heaps (creditors by positive net amount, debtors by absolute negative debt).
Pop top of each heap, settle min(credit, debt), and push back any remainder.
Time Complexity: O(n log n) where n is the number of non-zero members.
Space Complexity: O(n) space for max-heaps.
Correctness: Always resolves all debts in at most n - 1 transactions; drives every member's balance to zero.
"""

import time
from typing import Dict, List, Any
from app.algorithms.heap import MaxHeap

def settle_greedy(balances: Dict[str, int]) -> Dict[str, Any]:
    """
    Settles group debts using two MaxHeaps (greedy strategy).
    
    :param balances: Dict of {member_id: net_paise}.
    :return: Dict containing transactions, txn_count, total_moved_paise, runtime_ms.
    """
    t0 = time.perf_counter()

    creditors = MaxHeap()
    debtors = MaxHeap()

    for m_id, net in balances.items():
        if net > 0:
            creditors.push(net, m_id)
        elif net < 0:
            debtors.push(abs(net), m_id)

    transactions = []
    total_moved = 0

    while len(creditors) > 0 and len(debtors) > 0:
        c_amt, c_id = creditors.pop()
        d_amt, d_id = debtors.pop()

        settle_amt = min(c_amt, d_amt)

        transactions.append({
            "from_member": d_id,
            "to_member": c_id,
            "amount_paise": settle_amt
        })
        total_moved += settle_amt

        rem_c = c_amt - settle_amt
        rem_d = d_amt - settle_amt

        if rem_c > 0:
            creditors.push(rem_c, c_id)
        if rem_d > 0:
            debtors.push(rem_d, d_id)

    t1 = time.perf_counter()
    runtime_ms = (t1 - t0) * 1000.0

    return {
        "method": "greedy",
        "transactions": transactions,
        "txn_count": len(transactions),
        "total_moved_paise": total_moved,
        "runtime_ms": round(runtime_ms, 3)
    }
