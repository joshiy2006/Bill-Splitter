"""
Optimal Minimum-Transaction Debt Settlement using Bitmask Dynamic Programming.

Strategy: Bitmask DP over subset states to find maximum number of disjoint zero-sum subsets.
Time Complexity: O(m * 2^m) where m is the number of non-zero members (m <= 18).
Space Complexity: O(2^m) space for DP tables and parent tracking.
Correctness: Proved by graph theory that min transactions = m - max_zero_sum_subsets.
"""

import time
from typing import Dict, List, Any, Tuple
from app.algorithms.greedy import settle_greedy

class DpSizeError(Exception):
    """Raised when number of non-zero members exceeds maximum allowed for Bitmask DP (m > 18)."""
    pass

def settle_dp(balances: Dict[str, int]) -> Dict[str, Any]:
    """
    Settles group debts with globally optimal minimum transaction count using Bitmask DP.
    
    :param balances: Dict of {member_id: net_paise}.
    :return: Dict containing transactions, txn_count, total_moved_paise, runtime_ms, subsets_found.
    """
    t0 = time.perf_counter()

    # Filter out zero-balance members
    non_zero_items = sorted([(m, bal) for m, bal in balances.items() if bal != 0], key=lambda x: x[0])
    m = len(non_zero_items)

    if m == 0:
        t1 = time.perf_counter()
        return {
            "method": "dp",
            "transactions": [],
            "txn_count": 0,
            "total_moved_paise": 0,
            "runtime_ms": round((t1 - t0) * 1000.0, 3),
            "zero_sum_subsets": 0
        }

    if m > 18:
        raise DpSizeError(f"Number of non-zero members ({m}) exceeds maximum limit (18) for Bitmask DP")

    member_ids = [item[0] for item in non_zero_items]
    net_vals = [item[1] for item in non_zero_items]

    num_masks = 1 << m

    # Precompute subset sums
    sums = [0] * num_masks
    for mask in range(1, num_masks):
        # find lowest set bit index
        lsb = (mask & -mask).bit_length() - 1
        sums[mask] = sums[mask ^ (1 << lsb)] + net_vals[lsb]

    # DP array & parent array for reconstruction
    dp = [0] * num_masks
    parent = [-1] * num_masks

    for mask in range(1, num_masks):
        max_subsets = 0
        best_i = -1
        
        # Iterate over all bits set in mask
        temp = mask
        while temp > 0:
            lsb = (temp & -temp).bit_length() - 1
            prev_mask = mask ^ (1 << lsb)
            sub_val = dp[prev_mask]
            
            if sub_val >= max_subsets:
                max_subsets = sub_val
                best_i = lsb
                
            temp &= temp - 1

        is_zero_sum = 1 if sums[mask] == 0 else 0
        dp[mask] = max_subsets + is_zero_sum
        parent[mask] = best_i

    # Reconstruct zero-sum subset partition
    full_mask = num_masks - 1
    total_zero_sum_subsets = dp[full_mask]

    # Trace back member removal sequence
    curr_mask = full_mask
    ordering = []
    while curr_mask > 0:
        bit = parent[curr_mask]
        ordering.append(bit)
        curr_mask ^= (1 << bit)

    # Group into zero-sum components
    groups: List[List[int]] = []
    current_group: List[int] = []
    running_sum = 0

    for bit in ordering:
        current_group.append(bit)
        running_sum += net_vals[bit]
        if running_sum == 0:
            groups.append(current_group)
            current_group = []

    if current_group:
        groups.append(current_group)

    # For each zero-sum group, run greedy settlement
    all_transactions = []
    total_moved = 0

    for grp in groups:
        grp_balances = {member_ids[bit]: net_vals[bit] for bit in grp}
        grp_res = settle_greedy(grp_balances)
        all_transactions.extend(grp_res["transactions"])
        total_moved += grp_res["total_moved_paise"]

    t1 = time.perf_counter()
    runtime_ms = (t1 - t0) * 1000.0

    return {
        "method": "dp",
        "transactions": all_transactions,
        "txn_count": len(all_transactions),
        "total_moved_paise": total_moved,
        "runtime_ms": round(runtime_ms, 3),
        "zero_sum_subsets": total_zero_sum_subsets
    }
