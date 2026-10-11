"""
Balanced Item Allocation / Partition DP using big-int subset-sum bitsets.

Strategy: Dynamic Programming subset-sum via Python arbitrary-precision big-int bitsets.
Time Complexity: O(n * (sum / gcd)) bitwise operations.
Space Complexity: O(n * (sum / gcd)) for snapshot history.
Correctness: Bitset bit i is set if sum i is achievable; backtracking finds exact subset closest to total/2.
"""

import math
from functools import reduce
from typing import List, Dict, Any, Tuple

def balanced_partition(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Partitions items into two groups minimizing the difference between their total amounts.
    
    :param items: List of dicts with id, description/name, amount_paise.
    :return: Dict containing group_1, group_2, group_1_total, group_2_total, difference.
    """
    if not items:
        return {
            "group_1": [],
            "group_2": [],
            "group_1_total": 0,
            "group_2_total": 0,
            "difference": 0
        }

    amounts = [int(item["amount_paise"]) for item in items]
    total_amount = sum(amounts)

    if total_amount == 0:
        return {
            "group_1": items,
            "group_2": [],
            "group_1_total": 0,
            "group_2_total": 0,
            "difference": 0
        }

    # Reduce amounts by GCD to minimize bitset size
    all_gcd = reduce(math.gcd, amounts)
    scaled_amounts = [a // all_gcd for a in amounts]
    scaled_target = (total_amount // all_gcd) // 2

    # Bitset subset-sum DP with per-item snapshots
    # reachable integer bit mask: bit s is 1 if scaled sum s is reachable
    reachable = 1
    snapshots: List[int] = [reachable]

    for w in scaled_amounts:
        reachable |= (reachable << w)
        snapshots.append(reachable)

    # Find closest reachable sum <= scaled_target
    best_scaled_sum = 0
    for s in range(scaled_target, -1, -1):
        if (reachable & (1 << s)) != 0:
            best_scaled_sum = s
            break

    # Backtrack to reconstruct items in group 1
    group_1_indices = set()
    curr_sum = best_scaled_sum

    for i in range(len(items) - 1, -1, -1):
        w = scaled_amounts[i]
        prev_snap = snapshots[i]

        # Check if curr_sum was reached without item i
        if (prev_snap & (1 << curr_sum)) != 0:
            # Item i not included
            pass
        else:
            # Item i was included
            group_1_indices.add(i)
            curr_sum -= w

    group_1 = [items[i] for i in range(len(items)) if i in group_1_indices]
    group_2 = [items[i] for i in range(len(items)) if i not in group_1_indices]

    sum_1 = sum(int(item["amount_paise"]) for item in group_1)
    sum_2 = sum(int(item["amount_paise"]) for item in group_2)

    return {
        "group_1": group_1,
        "group_2": group_2,
        "group_1_total": sum_1,
        "group_2_total": sum_2,
        "difference": abs(sum_1 - sum_2)
    }
