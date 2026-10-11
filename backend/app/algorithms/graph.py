"""
Directed debt graph, cycle detection via DFS coloring, and cycle cancellation.

Strategy: DFS cycle detection using 3-color code (White=0, Grey=1, Black=2) and parent pointers.
Time Complexity: O(V * (V + E)) worst case to cancel all cycles.
Space Complexity: O(V + E) for adjacency graph representation.
Correctness: Subtracting min edge weight along a directed cycle preserves net balances for all nodes.
"""

from typing import Dict, List, Tuple, Set, Optional, Any

class DebtGraph:
    """
    Adjacency list representation of directed weighted debt graph.
    Edges (u, v) with weight w represent u owes v amount w.
    """
    def __init__(self):
        self.adj: Dict[str, Dict[str, int]] = {}

    def add_edge(self, u: str, v: str, w: int) -> None:
        if u == v or w <= 0:
            return
        if u not in self.adj:
            self.adj[u] = {}
        if v not in self.adj:
            self.adj[v] = {}
        self.adj[u][v] = self.adj[u].get(v, 0) + w

    def remove_edge(self, u: str, v: str) -> None:
        if u in self.adj and v in self.adj[u]:
            del self.adj[u][v]

    def get_nodes(self) -> Set[str]:
        nodes = set(self.adj.keys())
        for u in self.adj:
            for v in self.adj[u]:
                nodes.add(v)
        return nodes

    def to_edge_list(self) -> List[Dict[str, Any]]:
        edges = []
        for u in sorted(self.adj.keys()):
            for v in sorted(self.adj[u].keys()):
                w = self.adj[u][v]
                if w > 0:
                    edges.append({"from_member": u, "to_member": v, "amount_paise": w})
        return edges


def find_cycle(graph: DebtGraph) -> Optional[List[str]]:
    """
    Finds a single directed cycle using DFS 3-coloring.
    White = 0 (unvisited), Grey = 1 (visiting), Black = 2 (visited).
    
    :return: List of node IDs representing the cycle [v1, v2, ..., vk, v1] or None if acyclic.
    """
    nodes = list(graph.get_nodes())
    color: Dict[str, int] = {n: 0 for n in nodes}
    parent: Dict[str, Optional[str]] = {n: None for n in nodes}

    cycle_path: Optional[List[str]] = None

    def dfs(u: str) -> bool:
        nonlocal cycle_path
        color[u] = 1

        if u in graph.adj:
            for v, weight in sorted(graph.adj[u].items()):
                if weight <= 0:
                    continue
                if color[v] == 1:
                    # Found back edge u -> v (cycle detected)
                    path = [v, u]
                    curr = u
                    while curr != v and parent[curr] is not None:
                        curr = parent[curr]
                        path.append(curr)
                    path.reverse()
                    cycle_path = path
                    return True
                elif color[v] == 0:
                    parent[v] = u
                    if dfs(v):
                        return True

        color[u] = 2
        return False

    for node in sorted(nodes):
        if color[node] == 0:
            if dfs(node):
                return cycle_path

    return None


def cancel_cycles(graph: DebtGraph) -> Tuple[DebtGraph, List[Dict[str, Any]]]:
    """
    Repeatedly finds cycles in the graph and cancels them by subtracting the minimum
    edge weight around each cycle until the graph becomes acyclic.
    
    Strategy: Iterative DFS cycle detection and bottleneck subtraction.
    Time Complexity: O(V * (V + E)) worst case.
    Space Complexity: O(V + E).
    Correctness: Cyclic debt reduction maintains invariant that net balance of every node remains unchanged.
    
    :return: Tuple of (simplified DebtGraph, list of cancelled cycle records).
    """
    cancelled_cycles: List[Dict[str, Any]] = []

    while True:
        cycle = find_cycle(graph)
        if not cycle:
            break

        # Calculate minimum bottleneck edge weight in the cycle
        # cycle is [v1, v2, ..., vk, v1]
        bottleneck = float('inf')
        for i in range(len(cycle) - 1):
            u, v = cycle[i], cycle[i + 1]
            w = graph.adj[u][v]
            if w < bottleneck:
                bottleneck = w

        bottleneck_int = int(bottleneck)

        # Subtract bottleneck from all cycle edges
        for i in range(len(cycle) - 1):
            u, v = cycle[i], cycle[i + 1]
            graph.adj[u][v] -= bottleneck_int
            if graph.adj[u][v] == 0:
                graph.remove_edge(u, v)

        cancelled_cycles.append({
            "nodes": cycle[:-1],
            "bottleneck_paise": bottleneck_int
        })

    return graph, cancelled_cycles
