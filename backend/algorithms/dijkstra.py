from typing import List, Dict, Set, Tuple, Optional
from schemas import DijkstraRequest, DijkstraResponse, DijkstraStep

def run_dijkstra(request: DijkstraRequest) -> DijkstraResponse:
    nodes = [node.id for node in request.graph.nodes]
    edges = request.graph.edges
    
    # Adjacency list: node -> list of (neighbor, weight)
    adj: Dict[str, List[Tuple[str, float]]] = {n: [] for n in nodes}
    for e in edges:
        # Assuming directed edges for now, but usually routing is undirected
        # If undirected, need to add both ways, let's assume directed as per graph standard
        # The PDF says "Given graph G=(V,E) with positive edge weights... relax every outgoing edge"
        # Often Distance Vector and Dijkstra in these contexts use undirected links if not specified, 
        # or maybe the edges array explicitly includes both directions if it's undirected.
        # Let's just use the directed edges as provided. If it's undirected, the frontend should provide both.
        adj[e.source].append((e.target, e.weight))
        
    distances: Dict[str, Optional[float]] = {n: None for n in nodes}
    predecessors: Dict[str, Optional[str]] = {n: None for n in nodes}
    
    source = request.source
    if source in distances:
        distances[source] = 0.0
        
    visited: Set[str] = set()
    steps: List[DijkstraStep] = []
    step_index = 0
    
    # Initial state step
    steps.append(DijkstraStep(
        stepIndex=step_index,
        currentNode=None,
        visited=list(visited),
        distances=distances.copy(),
        predecessors=predecessors.copy(),
        relaxedEdges=[],
        description="Initialization: Source distance set to 0, all others to infinity."
    ))
    
    while len(visited) < len(nodes):
        # Find unvisited node with minimum distance
        min_dist = float('inf')
        u = None
        for n in nodes:
            if n not in visited and distances[n] is not None and distances[n] < min_dist:
                min_dist = distances[n]
                u = n
                
        if u is None:
            # Remaining nodes are unreachable
            break
            
        visited.add(u)
        step_index += 1
        
        relaxed_edges = []
        
        for v, weight in adj[u]:
            if v not in visited:
                new_dist = distances[u] + weight
                if distances[v] is None or new_dist < distances[v]:
                    distances[v] = new_dist
                    predecessors[v] = u
                    relaxed_edges.append({'source': u, 'target': v})
                    
        desc = f"Node {u} finalized. Relaxed {len(relaxed_edges)} outgoing edge(s)."
        if len(relaxed_edges) == 0:
            desc = f"Node {u} finalized. No edges to relax."
            
        steps.append(DijkstraStep(
            stepIndex=step_index,
            currentNode=u,
            visited=list(visited),
            distances=distances.copy(),
            predecessors=predecessors.copy(),
            relaxedEdges=relaxed_edges,
            description=desc
        ))

    final_path = None
    final_distance = None
    if request.destination and request.destination in nodes:
        dest = request.destination
        final_distance = distances[dest]
        if final_distance is not None:
            path = []
            curr = dest
            while curr is not None:
                path.insert(0, curr)
                curr = predecessors[curr]
            final_path = path

    return DijkstraResponse(
        steps=steps,
        finalPath=final_path,
        finalDistance=final_distance
    )
