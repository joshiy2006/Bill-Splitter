"""
Expense search and indexing using Trie prefix search and Hash-Map indexes.

Strategy: Trie prefix tree for description/member autocomplete + hash-map category/payer inverted index.
Time Complexity: O(L) for Trie prefix search of query length L; O(K) set intersections for filtered queries.
Space Complexity: O(W * L) where W is number of words, L is max word length.
Correctness: Intersects non-empty filter candidate sets starting with smallest set to minimize comparison steps.
"""

import re
from typing import Dict, List, Set, Any, Optional, Tuple

class TrieNode:
    def __init__(self):
        self.children: Dict[str, 'TrieNode'] = {}
        self.is_end: bool = False
        self.expense_ids: Set[str] = set()


class Trie:
    """
    Trie (prefix tree) for word prefix matching and autocomplete suggestions.
    """
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, expense_id: str) -> None:
        """
        Inserts a word into the Trie associated with an expense_id.
        Complexity: O(L) time where L is word length.
        """
        word = word.lower().strip()
        if not word:
            return
        curr = self.root
        for char in word:
            if char not in curr.children:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
            curr.expense_ids.add(expense_id)
        curr.is_end = True

    def search_prefix(self, prefix: str, limit: int = 10) -> Set[str]:
        """
        Returns set of expense_ids matching the given prefix.
        Complexity: O(L + K) time.
        """
        prefix = prefix.lower().strip()
        if not prefix:
            return set()
        curr = self.root
        for char in prefix:
            if char not in curr.children:
                return set()
            curr = curr.children[char]
        return curr.expense_ids

    def autocomplete(self, prefix: str, limit: int = 5) -> List[str]:
        """
        Returns list of matching completed words for a prefix.
        """
        prefix = prefix.lower().strip()
        if not prefix:
            return []
        curr = self.root
        for char in prefix:
            if char not in curr.children:
                return []
            curr = curr.children[char]

        results: List[str] = []

        def _dfs(node: TrieNode, path: str):
            if len(results) >= limit:
                return
            if node.is_end:
                results.append(path)
            for char, next_node in sorted(node.children.items()):
                _dfs(next_node, path + char)

        _dfs(curr, prefix)
        return results


class ExpenseIndex:
    """
    Inverted index using hash-maps and Trie for expense filtering.
    """
    def __init__(self):
        self.trie = Trie()
        self.category_index: Dict[str, Set[str]] = {}
        self.payer_index: Dict[str, Set[str]] = {}
        self.all_expense_ids: Set[str] = set()

    def build(self, expenses: List[Dict[str, Any]], member_map: Optional[Dict[str, str]] = None) -> None:
        """
        Builds inverted hash-map indexes and populates the Trie.
        """
        self.trie = Trie()
        self.category_index.clear()
        self.payer_index.clear()
        self.all_expense_ids.clear()

        for exp in expenses:
            e_id = str(exp["id"])
            self.all_expense_ids.add(e_id)

            # Category index
            cat = str(exp.get("category", "general")).lower()
            if cat not in self.category_index:
                self.category_index[cat] = set()
            self.category_index[cat].add(e_id)

            # Payer index
            payer = str(exp.get("paid_by"))
            if payer not in self.payer_index:
                self.payer_index[payer] = set()
            self.payer_index[payer].add(e_id)

            # Index description words into Trie
            desc = str(exp.get("description", ""))
            words = re.findall(r'\w+', desc)
            for w in words:
                self.trie.insert(w, e_id)

            # Also index payer name if member_map provided
            if member_map and payer in member_map:
                p_name = member_map[payer]
                for w in re.findall(r'\w+', p_name):
                    self.trie.insert(w, e_id)


def filter_expenses(
    index: ExpenseIndex,
    expenses_dict: Dict[str, Dict[str, Any]],
    q: Optional[str] = None,
    category: Optional[str] = None,
    payer: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    min_amount: Optional[int] = None,
    max_amount: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Filters expenses by intersecting candidate sets starting with the smallest set.
    
    :return: List of filtered expense dicts.
    """
    candidate_sets: List[Set[str]] = []

    if q and q.strip():
        q_ids = index.trie.search_prefix(q)
        candidate_sets.append(q_ids)

    if category and category.strip() and category.lower() != "all":
        cat_ids = index.category_index.get(category.lower(), set())
        candidate_sets.append(cat_ids)

    if payer and payer.strip() and payer.lower() != "all":
        payer_ids = index.payer_index.get(payer, set())
        candidate_sets.append(payer_ids)

    if not candidate_sets:
        matched_ids = set(index.all_expense_ids)
    else:
        # Sort candidate sets by size ascending to optimize intersection speed
        candidate_sets.sort(key=len)
        matched_ids = set(candidate_sets[0])
        for s in candidate_sets[1:]:
            matched_ids.intersection_update(s)

    # Further filter by range bounds (date range, amount range)
    result = []
    for e_id in matched_ids:
        if e_id not in expenses_dict:
            continue
        exp = expenses_dict[e_id]

        amt = int(exp.get("amount_paise", 0))
        if min_amount is not None and amt < min_amount:
            continue
        if max_amount is not None and amt > max_amount:
            continue

        e_date = str(exp.get("expense_date", ""))
        if date_from and e_date < date_from:
            continue
        if date_to and e_date > date_to:
            continue

        result.append(exp)

    # Sort results by date descending
    result.sort(key=lambda x: str(x.get("expense_date", "")), reverse=True)
    return result
