"""
Net balance computation and raw pairwise debt graph construction.

Strategy: Hash map aggregation of paid expenses, splits, and settlement payments.
Time Complexity: O(E + S + P) where E is expenses, S is splits, P is payments.
Space Complexity: O(M^2) where M is number of members.
Correctness: Conservation of money invariant guarantees sum of net balances is strictly zero.
"""

from typing import List, Dict, Tuple, Any

def net_balances(
    members: List[str],
    expenses: List[Dict[str, Any]],
    splits: List[Dict[str, Any]],
    payments: List[Dict[str, Any]]
) -> Dict[str, int]:
    """
    Computes net balance per member in integer paise.
    net = paid_by_expenses - owed_by_splits + payments_sent - payments_received
    
    net > 0 => Creditor (is owed money)
    net < 0 => Debtor (owes money)
    
    :param members: List of member IDs.
    :param expenses: List of expense dicts (id, paid_by, amount_paise).
    :param splits: List of split dicts (expense_id, member_id, owed_paise).
    :param payments: List of payment dicts (from_member, to_member, amount_paise).
    :return: Dict mapping member_id to net_paise.
    """
    balances: Dict[str, int] = {m: 0 for m in members}

    for e in expenses:
        payer = str(e["paid_by"])
        amount = int(e["amount_paise"])
        if payer not in balances:
            balances[payer] = 0
        balances[payer] += amount

    for s in splits:
        member = str(s["member_id"])
        owed = int(s["owed_paise"])
        if member not in balances:
            balances[member] = 0
        balances[member] -= owed

    for p in payments:
        from_m = str(p["from_member"])
        to_m = str(p["to_member"])
        amt = int(p["amount_paise"])
        if from_m not in balances:
            balances[from_m] = 0
        if to_m not in balances:
            balances[to_m] = 0
        balances[from_m] += amt
        balances[to_m] -= amt

    total_sum = sum(balances.values())
    assert total_sum == 0, f"Net balances do not sum to 0! Got {total_sum}"
    return balances


def pairwise_debts(
    expenses: List[Dict[str, Any]],
    splits: List[Dict[str, Any]],
    payments: List[Dict[str, Any]]
) -> Dict[Tuple[str, str], int]:
    """
    Builds raw pairwise debts mapping (from_member, to_member) -> amount_paise.
    Each split row creates a debt edge from participant (from_member) to payer (to_member).
    Payments subtract from pairwise debts.
    
    :return: Dict of (from_member, to_member) -> net_debt_paise > 0.
    """
    # Map expense_id to paid_by
    expense_payers = {str(e["id"]): str(e["paid_by"]) for e in expenses}

    raw_debts: Dict[Tuple[str, str], int] = {}

    for s in splits:
        exp_id = str(s["expense_id"])
        payer = expense_payers.get(exp_id)
        participant = str(s["member_id"])
        owed = int(s["owed_paise"])

        if payer and participant != payer and owed > 0:
            pair = (participant, payer)
            raw_debts[pair] = raw_debts.get(pair, 0) + owed

    # Apply direct payments
    for p in payments:
        from_m = str(p["from_member"])
        to_m = str(p["to_member"])
        amt = int(p["amount_paise"])

        pair = (from_m, to_m)
        rev_pair = (to_m, from_m)

        if pair in raw_debts:
            raw_debts[pair] -= amt
            if raw_debts[pair] <= 0:
                leftover = -raw_debts[pair]
                del raw_debts[pair]
                if leftover > 0:
                    raw_debts[rev_pair] = raw_debts.get(rev_pair, 0) + leftover
        else:
            raw_debts[rev_pair] = raw_debts.get(rev_pair, 0) - amt

    # Filter out zero or negative debts
    result: Dict[Tuple[str, str], int] = {}
    for (u, v), w in raw_debts.items():
        if u != v and w > 0:
            result[(u, v)] = w

    return result
