"""
Exact integer split resolution for group expenses using Largest Remainder Method.

Strategy: Largest Remainder Method (Hare-Niemeyer method) for percentage/share splits, integer division with deterministic remainder distribution for equal splits.
Time Complexity: O(k log k) due to remainder sorting where k is participant count.
Space Complexity: O(k) space for candidate shares.
Correctness: Always returns whole integer paise summing EXACTLY to amount_paise, breaking remainder ties deterministically by member_id.
"""

from typing import List, Dict, Any

def resolve_split(amount_paise: int, split_type: str, participants: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Resolves participant splits into exact integer paise summing strictly to amount_paise.
    
    :param amount_paise: Total expense amount in paise (integer).
    :param split_type: 'equal' | 'exact' | 'percentage' | 'shares'
    :param participants: List of dicts containing member_id and optional split parameters.
    :return: List of dicts with key member_id and resolved owed_paise.
    """
    if amount_paise <= 0:
        raise ValueError("Amount paise must be positive integer")
    if not participants:
        raise ValueError("Participants list cannot be empty")

    k = len(participants)
    # Sort participants deterministically by member_id
    sorted_parts = sorted(participants, key=lambda x: str(x["member_id"]))

    if split_type == "equal":
        base = amount_paise // k
        rem = amount_paise % k
        
        result = []
        for i, p in enumerate(sorted_parts):
            owed = base + (1 if i < rem else 0)
            result.append({
                "member_id": p["member_id"],
                "owed_paise": owed,
                "share_value": None
            })
        return result

    elif split_type == "exact":
        total_owed = sum(int(p.get("owed_paise", 0)) for p in sorted_parts)
        if total_owed != amount_paise:
            raise ValueError(f"Exact splits sum ({total_owed}) does not equal total amount ({amount_paise})")
        return [
            {
                "member_id": p["member_id"],
                "owed_paise": int(p.get("owed_paise", 0)),
                "share_value": float(p.get("owed_paise", 0))
            }
            for p in sorted_parts
        ]

    elif split_type == "percentage":
        total_pct = sum(float(p.get("percentage", 0.0)) for p in sorted_parts)
        if abs(total_pct - 100.0) > 1e-6:
            raise ValueError(f"Percentages must sum to 100, got {total_pct}")

        candidates = []
        sum_floored = 0
        for p in sorted_parts:
            pct = float(p.get("percentage", 0.0))
            exact_val = (pct / 100.0) * amount_paise
            floored = int(exact_val)
            rem = exact_val - floored
            candidates.append({
                "member_id": p["member_id"],
                "floored": floored,
                "rem": rem,
                "pct": pct
            })
            sum_floored += floored

        deficit = amount_paise - sum_floored
        # Sort by remainder descending, then member_id ascending for deterministic tie-breaking
        candidates.sort(key=lambda c: (-c["rem"], str(c["member_id"])))

        for i in range(deficit):
            candidates[i]["floored"] += 1

        # Re-sort to original member_id order
        candidates.sort(key=lambda c: str(c["member_id"]))
        return [
            {
                "member_id": c["member_id"],
                "owed_paise": c["floored"],
                "share_value": c["pct"]
            }
            for c in candidates
        ]

    elif split_type == "shares":
        total_shares = sum(float(p.get("shares", 0.0)) for p in sorted_parts)
        if total_shares <= 0:
            raise ValueError("Total shares must be positive")

        candidates = []
        sum_floored = 0
        for p in sorted_parts:
            s_val = float(p.get("shares", 0.0))
            exact_val = (s_val / total_shares) * amount_paise
            floored = int(exact_val)
            rem = exact_val - floored
            candidates.append({
                "member_id": p["member_id"],
                "floored": floored,
                "rem": rem,
                "shares": s_val
            })
            sum_floored += floored

        deficit = amount_paise - sum_floored
        candidates.sort(key=lambda c: (-c["rem"], str(c["member_id"])))

        for i in range(deficit):
            candidates[i]["floored"] += 1

        candidates.sort(key=lambda c: str(c["member_id"]))
        return [
            {
                "member_id": c["member_id"],
                "owed_paise": c["floored"],
                "share_value": c["shares"]
            }
            for c in candidates
        ]

    else:
        raise ValueError(f"Unknown split_type: {split_type}")
