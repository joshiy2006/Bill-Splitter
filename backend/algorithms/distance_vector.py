from typing import List, Dict, Optional, Any
from schemas import DVRequest, DVResponse, DVStep, DVTableEntry

def run_distance_vector(request: DVRequest) -> DVResponse:
    nodes = sorted([node.id for node in request.graph.nodes])
    edges = request.graph.edges
    
    link_costs: Dict[str, Dict[str, Optional[float]]] = {n: {} for n in nodes}
    neighbor_dvs: Dict[str, Dict[str, Dict[str, Optional[float]]]] = {n: {} for n in nodes}
    tables: Dict[str, Dict[str, DVTableEntry]] = {n: {} for n in nodes}
    
    for n in nodes:
        for d in nodes:
            if n == d:
                tables[n][d] = DVTableEntry(cost=0.0, nextHop=n)
            else:
                tables[n][d] = DVTableEntry(cost=None, nextHop=None)
                
    for e in edges:
        link_costs[e.source][e.target] = e.weight
        link_costs[e.target][e.source] = e.weight
        if e.target not in neighbor_dvs[e.source]:
            neighbor_dvs[e.source][e.target] = {d: None for d in nodes}
        if e.source not in neighbor_dvs[e.target]:
            neighbor_dvs[e.target][e.source] = {d: None for d in nodes}

    def copy_tables():
        res = {}
        for n in nodes:
            res[n] = {d: DVTableEntry(cost=tables[n][d].cost, nextHop=tables[n][d].nextHop) for d in nodes}
        return res

    def recompute_table(Q: str) -> List[Dict[str, str]]:
        changed = []
        for d in nodes:
            if d == Q:
                continue
            
            min_cost = None
            best_next = None
            
            # Sort neighbors to ensure deterministic tie-breaking
            neighbors = sorted(list(link_costs[Q].keys()))
            for M in neighbors:
                cost_QM = link_costs[Q][M]
                if cost_QM is None:
                    continue # link failed
                    
                adv_MD = neighbor_dvs[Q][M].get(d)
                if adv_MD is not None:
                    total_cost = cost_QM + adv_MD
                    if min_cost is None or total_cost < min_cost:
                        min_cost = total_cost
                        best_next = M
                        
            old_entry = tables[Q][d]
            if old_entry.cost != min_cost or old_entry.nextHop != best_next:
                tables[Q][d] = DVTableEntry(cost=min_cost, nextHop=best_next)
                changed.append({"node": Q, "dest": d})
                
        return changed

    steps: List[DVStep] = []
    step_index = 0
    converged = False
    rounds_run = 0
    
    # Emit initial state
    steps.append(DVStep(
        stepIndex=step_index,
        round=0,
        broadcastingNode=None,
        tables=copy_tables(),
        changedEntries=[],
        description="Initialization: Nodes only know distance to themselves."
    ))

    # Keep track of which nodes have changed and need to broadcast.
    # Initially all nodes need to broadcast.
    needs_broadcast = {n: True for n in nodes}

    for round_num in range(1, request.maxRounds + 1):
        rounds_run = round_num
        round_changed = False
        
        # Apply events for this round
        round_events = [ev for ev in request.events if ev.atRound == round_num]
        for ev in round_events:
            u, v = ev.edge
            old_w = link_costs[u].get(v)
            link_costs[u][v] = ev.newWeight
            link_costs[v][u] = ev.newWeight
            
            c1 = recompute_table(u)
            c2 = recompute_table(v)
            if c1: needs_broadcast[u] = True
            if c2: needs_broadcast[v] = True
            if c1 or c2:
                round_changed = True
                
            step_index += 1
            desc = f"Event: Link {u}-{v} weight changed from {old_w} to {ev.newWeight}"
            if ev.newWeight is None:
                desc = f"Event: Link {u}-{v} failed"
                
            steps.append(DVStep(
                stepIndex=step_index,
                round=round_num,
                broadcastingNode=None,
                tables=copy_tables(),
                changedEntries=c1 + c2,
                event=desc,
                description=desc
            ))
            
        # Nodes broadcast
        next_needs_broadcast = {n: False for n in nodes}
        any_broadcasted = False
        
        for N in nodes:
            if not needs_broadcast[N]:
                continue
                
            any_broadcasted = True
            changed_in_broadcast = []
            neighbors = sorted(list(link_costs[N].keys()))
            for Q in neighbors:
                if link_costs[N][Q] is not None:
                    advertised = {}
                    for d in nodes:
                        if request.poisonReverse and tables[N][d].nextHop == Q:
                            advertised[d] = None
                        else:
                            advertised[d] = tables[N][d].cost
                    neighbor_dvs[Q][N] = advertised
                    
                    changes = recompute_table(Q)
                    if changes:
                        next_needs_broadcast[Q] = True
                        changed_in_broadcast.extend(changes)
                        
            if changed_in_broadcast:
                round_changed = True
                
            step_index += 1
            desc = f"Node {N} broadcasts its distance vector."
            steps.append(DVStep(
                stepIndex=step_index,
                round=round_num,
                broadcastingNode=N,
                tables=copy_tables(),
                changedEntries=changed_in_broadcast,
                event=None,
                description=desc
            ))
            
        if not any_broadcasted and not round_changed:
            converged = True
            break
            
        needs_broadcast = next_needs_broadcast

    return DVResponse(
        steps=steps,
        converged=converged,
        roundsRun=rounds_run
    )
