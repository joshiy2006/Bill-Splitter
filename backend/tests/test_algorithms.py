"""
Comprehensive algorithm tests for backend/app/algorithms package.
Covers splits, balances, cycle cancellation, greedy vs optimal DP, counterexample fixture,
partition DP, scheduler, and search trie.
"""

import pytest
from hypothesis import given, strategies as st
from app.algorithms.heap import MaxHeap, MinHeap, top_k
from app.algorithms.splits import resolve_split
from app.algorithms.balances import net_balances, pairwise_debts
from app.algorithms.graph import DebtGraph, find_cycle, cancel_cycles
from app.algorithms.greedy import settle_greedy
from app.algorithms.dp_optimal import settle_dp, DpSizeError
from app.algorithms.partition import balanced_partition
from app.algorithms.scheduler import schedule_payments
from app.algorithms.search import Trie, ExpenseIndex, filter_expenses

# ============================================================
# 1. Heap Tests
# ============================================================
def test_max_heap():
    heap = MaxHeap()
    heap.push(10, "A")
    heap.push(50, "B")
    heap.push(20, "C")
    
    assert len(heap) == 3
    assert heap.peek() == (50, "B")
    
    val, item = heap.pop()
    assert (val, item) == (50, "B")
    assert heap.pop() == (20, "C")
    assert heap.pop() == (10, "A")
    assert len(heap) == 0

def test_top_k():
    items = [{"name": "A", "val": 10}, {"name": "B", "val": 100}, {"name": "C", "val": 50}]
    res = top_k(items, 2, key=lambda x: x["val"])
    assert len(res) == 2
    assert res[0]["name"] == "B"
    assert res[1]["name"] == "C"

# ============================================================
# 2. Split Resolution Tests
# ============================================================
def test_splits_equal():
    parts = [{"member_id": "m1"}, {"member_id": "m2"}, {"member_id": "m3"}]
    res = resolve_split(100, "equal", parts)
    sum_owed = sum(r["owed_paise"] for r in res)
    assert sum_owed == 100
    # 100 // 3 = 33, rem = 1 => 34, 33, 33
    owed_vals = [r["owed_paise"] for r in res]
    assert owed_vals == [34, 33, 33]

def test_splits_percentage_rejection():
    parts = [{"member_id": "m1", "percentage": 50.0}, {"member_id": "m2", "percentage": 40.0}]
    with pytest.raises(ValueError, match="Percentages must sum to 100"):
        resolve_split(1000, "percentage", parts)

def test_splits_percentage_largest_remainder():
    parts = [
        {"member_id": "m1", "percentage": 33.3333},
        {"member_id": "m2", "percentage": 33.3333},
        {"member_id": "m3", "percentage": 33.3334},
    ]
    res = resolve_split(1000, "percentage", parts)
    assert sum(r["owed_paise"] for r in res) == 1000

# ============================================================
# 3. Balances & Debt Graph Tests
# ============================================================
def test_net_balances_sum_zero():
    members = ["m1", "m2", "m3"]
    expenses = [{"id": "e1", "paid_by": "m1", "amount_paise": 300}]
    splits = [
        {"expense_id": "e1", "member_id": "m1", "owed_paise": 100},
        {"expense_id": "e1", "member_id": "m2", "owed_paise": 100},
        {"expense_id": "e1", "member_id": "m3", "owed_paise": 100},
    ]
    payments = []
    bals = net_balances(members, expenses, splits, payments)
    assert sum(bals.values()) == 0
    assert bals["m1"] == 200
    assert bals["m2"] == -100
    assert bals["m3"] == -100

def test_cycle_cancellation():
    """
    Cycle cancellation: A -> B -> C -> A with equal weights becomes empty; net balances unchanged.
    """
    g = DebtGraph()
    g.add_edge("A", "B", 100)
    g.add_edge("B", "C", 100)
    g.add_edge("C", "A", 100)
    
    simplified, cancelled = cancel_cycles(g)
    assert len(cancelled) == 1
    assert cancelled[0]["bottleneck_paise"] == 100
    assert len(simplified.to_edge_list()) == 0

# ============================================================
# 4. Mandatory Counterexample Fixture (Greedy Sub-optimal vs DP Optimal)
# ============================================================
def test_mandatory_counterexample_fixture():
    """
    Mandatory counterexample fixture: balances [+400, +300, -300, -200, -200].
    Greedy returns 4 transactions; DP returns 3.
    This case proves greedy is not optimal. Assert it explicitly!
    """
    balances = {
        "m1": 400,
        "m2": 300,
        "m3": -300,
        "m4": -200,
        "m5": -200
    }
    greedy_res = settle_greedy(balances)
    dp_res = settle_dp(balances)

    assert greedy_res["txn_count"] == 4, f"Expected 4 greedy txns, got {greedy_res['txn_count']}"
    assert dp_res["txn_count"] == 3, f"Expected 3 DP txns, got {dp_res['txn_count']}"
    assert dp_res["txn_count"] < greedy_res["txn_count"]

    # Verify applying DP settlement drives balances to zero
    final_bals = dict(balances)
    for txn in dp_res["transactions"]:
        final_bals[txn["from_member"]] += txn["amount_paise"]
        final_bals[txn["to_member"]] -= txn["amount_paise"]
    assert all(val == 0 for val in final_bals.values())

# ============================================================
# 5. Brute Force Oracle for DP Settlement
# ============================================================
def enumerate_min_transactions_brute_force(balances: dict) -> int:
    """Helper oracle that enumerates zero-sum partitions for small m to find true min transactions."""
    non_zero = [v for v in balances.values() if v != 0]
    m = len(non_zero)
    if m == 0:
        return 0

    import itertools
    # Find all non-empty subsets with sum 0
    zero_subsets = []
    for r in range(1, m + 1):
        for combo in itertools.combinations(range(m), r):
            if sum(non_zero[i] for i in combo) == 0:
                zero_subsets.append(set(combo))

    # Find maximum number of mutually disjoint zero-sum subsets
    max_count = 0
    def backtrack(idx, count, used_mask):
        nonlocal max_count
        if count > max_count:
            max_count = count
        for i in range(idx, len(zero_subsets)):
            s = zero_subsets[i]
            s_mask = sum(1 << elem for elem in s)
            if (used_mask & s_mask) == 0:
                backtrack(i + 1, count + 1, used_mask | s_mask)

    backtrack(0, 0, 0)
    return m - max_count

def test_dp_matches_brute_force_oracle():
    test_cases = [
        {"a": 100, "b": -100},
        {"a": 100, "b": 200, "c": -300},
        {"a": 500, "b": 300, "c": -200, "d": -600},
        {"a": 400, "b": 300, "c": -300, "d": -200, "e": -200}, # counterexample
    ]
    for case in test_cases:
        oracle_min = enumerate_min_transactions_brute_force(case)
        dp_res = settle_dp(case)
        assert dp_res["txn_count"] == oracle_min

# ============================================================
# 6. Partition DP & Scheduler Tests
# ============================================================
def test_partition_dp():
    items = [
        {"id": "1", "name": "Item A", "amount_paise": 100},
        {"id": "2", "name": "Item B", "amount_paise": 200},
        {"id": "3", "name": "Item C", "amount_paise": 300},
    ]
    res = balanced_partition(items)
    assert res["difference"] == 0
    assert res["group_1_total"] == 300
    assert res["group_2_total"] == 300

def test_scheduler_priority():
    txns = [
        {"from_member": "a", "to_member": "b", "amount_paise": 100, "due_date": "2026-10-10"},
        {"from_member": "c", "to_member": "d", "amount_paise": 500, "due_date": "2026-10-05"},
    ]
    scheduled = schedule_payments(txns, today="2026-10-01")
    assert scheduled[0]["to_member"] == "d" # earlier due date gets priority 1
    assert scheduled[0]["priority"] == 1
    assert scheduled[1]["priority"] == 2

# ============================================================
# 7. Search & Trie Tests
# ============================================================
def test_trie_search():
    trie = Trie()
    trie.insert("Dinner", "e1")
    trie.insert("Drinks", "e2")
    trie.insert("Dining", "e3")

    ids = trie.search_prefix("din")
    assert "e1" in ids
    assert "e3" in ids
    assert "e2" not in ids

    auto = trie.autocomplete("di")
    assert "dining" in auto or "dinner" in auto

def test_filter_expenses():
    index = ExpenseIndex()
    expenses = [
        {"id": "e1", "description": "Goa Villa Rent", "category": "rent", "paid_by": "m1", "amount_paise": 6000000, "expense_date": "2026-10-01"},
        {"id": "e2", "description": "Seafood Shack Dinner", "category": "food", "paid_by": "m2", "amount_paise": 1200000, "expense_date": "2026-10-02"},
    ]
    exp_dict = {e["id"]: e for e in expenses}
    index.build(expenses)

    res = filter_expenses(index, exp_dict, q="Seafood", category="food")
    assert len(res) == 1
    assert res[0]["id"] == "e2"
