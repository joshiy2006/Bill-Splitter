# Comprehensive Algorithm Specifications & Proofs — Smart Bill-Splitting System

This document outlines the theoretical design, pseudocode, asymptotic analysis, correctness arguments, and empirical benchmarks for all algorithm components in the **Smart Bill-Splitting & Debt Settlement System** (Design and Analysis of Algorithms Assignment).

---

## 1. Greedy Debt Settlement (Two Max-Heaps)

- **Problem**: Given net integer balances for $n$ members where $\sum \text{net}_i = 0$, find a sequence of directed payment transactions that drives every member's balance to 0.
- **Strategy**: Maintain two custom Max-Heaps: `creditors` (storing members with positive balances sorted by credit amount) and `debtors` (storing members with negative balances sorted by absolute debt amount). At each step, pop the maximum creditor and maximum debtor, settle $\min(\text{credit}, \text{debt})$, push back any non-zero remainder, and repeat until both heaps are empty.
- **Time Complexity**: $O(n \log n)$ time.
- **Space Complexity**: $O(n)$ space for heap elements.
- **Correctness**: In each step, at least one member's balance is completely zeroed out and removed. Thus, the loop terminates in at most $n - 1$ transactions, conserving total money at each step.

### Pseudocode
```python
def settle_greedy(balances):
    creditors = MaxHeap()
    debtors = MaxHeap()
    for m, val in balances.items():
        if val > 0: creditors.push(val, m)
        elif val < 0: debtors.push(abs(val), m)
    
    transactions = []
    while creditors and debtors:
        c_amt, c_id = creditors.pop()
        d_amt, d_id = debtors.pop()
        settle_amt = min(c_amt, d_amt)
        transactions.append({"from": d_id, "to": c_id, "amount": settle_amt})
        if c_amt - settle_amt > 0: creditors.push(c_amt - settle_amt, c_id)
        if d_amt - settle_amt > 0: debtors.push(d_amt - settle_amt, d_id)
    return transactions
```

---

## 2. Optimal Minimum-Transaction Settlement (Bitmask Dynamic Programming)

- **Problem**: Minimize the number of transactions required to settle all debts.
- **Strategy**: Graph theory proves that minimum transactions $= m - k$, where $m$ is the number of non-zero members and $k$ is the maximum number of mutually disjoint zero-sum subsets. We use Bitmask DP over $2^m$ subset masks ($m \le 18$).
- **Recurrence**:
  $$\text{dp}[\text{mask}] = \max_{i \in \text{mask}} \left( \text{dp}[\text{mask} \setminus \{i\}] \right) + [ \text{sum}[\text{mask}] == 0 ]$$
- **Time Complexity**: $O(m \cdot 2^m)$ time.
- **Space Complexity**: $O(2^m)$ space.
- **Correctness**: Every zero-sum subset of size $s$ can be settled internally in $s - 1$ transactions. Maximizing disjoint zero-sum subsets maximizes $(m - k)$ savings.

### Why Greedy is NOT Always Optimal (Mandatory Counterexample)
Consider 5 members with net balances: `[+400, +300, -300, -200, -200]`:
- **Greedy Output (4 Transactions)**:
  1. `-300` pays `+400`: 300 (left `+100`)
  2. `-200` pays `+100`: 100 (left `-100`)
  3. `-100` pays `+300`: 100 (left `+200`)
  4. `-200` pays `+200`: 200
- **Optimal DP Output (3 Transactions)**:
  Partitions into two zero-sum subsets: `[+300, -300]` and `[+400, -200, -200]`.
  1. `-300` pays `+300`: 300
  2. `-200` pays `+400`: 200 (left `+200`)
  3. `-200` pays `+400`: 200

---

## 3. Directed Debt Network & DFS Cycle Cancellation

- **Problem**: Given raw pairwise debt edges, simplify cycle debts (e.g. $A \to B \to C \to A$) without changing any member's net balance.
- **Strategy**: Adjacency list `DebtGraph`. DFS 3-coloring (`White=0`, `Grey=1`, `Black=2`) finds directed back edges. When a cycle is found, compute the bottleneck edge weight $W_{\min}$, subtract $W_{\min}$ around the cycle, remove 0-weight edges, and repeat until graph is acyclic.
- **Time Complexity**: $O(V \cdot (V + E))$ worst case.
- **Space Complexity**: $O(V + E)$ space.
- **Correctness**: Subtracting a uniform amount $W$ along a directed cycle reduces $W$ from incoming and outgoing edges for every node in the cycle, leaving $\text{net}_i = \text{in}_i - \text{out}_i$ unchanged.

---

## 4. Split Resolution (Largest Remainder Method)

- **Problem**: Convert fractional/percentage/share splits into exact whole integer paise summing strictly to total expense amount.
- **Strategy**: Hare-Niemeyer Largest Remainder Method. Floor each participant's share $\lfloor \text{exact}_i \rfloor$, calculate fractional remainders $r_i = \text{exact}_i - \lfloor \text{exact}_i \rfloor$, sort candidates by $r_i$ descending (breaking ties deterministically by `member_id`), and distribute the leftover deficit 1 paise at a time.
- **Time Complexity**: $O(k \log k)$ time.
- **Space Complexity**: $O(k)$ space.
- **Correctness**: Sum of floored shares + deficit equals exact total amount; allocating extra paise by largest remainder minimizes global rounding distortion.

---

## 5. Balanced Item Allocation (Partition DP)

- **Problem**: Split a set of expense items between two people to minimize the absolute difference in total amounts paid.
- **Strategy**: Subset-sum DP using Python arbitrary-precision big-int bitsets (`reachable |= reachable << w`). Reduce item amounts by their greatest common divisor (GCD) to keep bitset small, then backtrack from total / 2.
- **Time Complexity**: $O(n \cdot (\text{sum} / \text{gcd}))$ bitwise operations.
- **Space Complexity**: $O(n \cdot (\text{sum} / \text{gcd}))$ snapshot space.
- **Correctness**: Bitset bit $s$ is 1 iff exact scaled sum $s$ is reachable by a subset of items. Backtracking reconstructs the optimal subset.

---

## 6. Priority Queue Smart Payment Scheduler

- **Problem**: Order pending settlement transactions by urgency.
- **Strategy**: MinHeap priority queue storing tuples `(due_date, -amount_paise)`. Pop in order and assign priorities $1, 2, 3, \dots$.
- **Time Complexity**: $O(t \log t)$ time.
- **Space Complexity**: $O(t)$ space.
- **Correctness**: Min-heap order guarantees earliest due date and highest payment amount are processed first.

---

## 7. Expense Search & Filtering (Trie + Inverted Hash-Map Index)

- **Problem**: Search expense descriptions and member names with autocomplete and multi-field filtering.
- **Strategy**: Trie prefix tree for description words and member names + inverted hash-map index `category -> set(ids)` and `payer -> set(ids)`. Intersects candidate sets starting with the smallest set.
- **Time Complexity**: $O(L + K)$ where $L$ is query length and $K$ is set intersection size.
- **Space Complexity**: $O(W \cdot L)$ for Trie nodes.
- **Correctness**: Set intersection of inverted index matches only items satisfying all query filters simultaneously.
