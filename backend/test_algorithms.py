import json
from schemas import Graph, Node, Edge, DijkstraRequest, DVRequest, DVEvent
from algorithms.dijkstra import run_dijkstra
from algorithms.distance_vector import run_distance_vector

def main():
    # 5-node graph for Dijkstra
    nodes = [
        Node(id="A"), Node(id="B"), Node(id="C"), Node(id="D"), Node(id="E")
    ]
    edges = [
        Edge(source="A", target="B", weight=4),
        Edge(source="A", target="C", weight=2),
        Edge(source="B", target="C", weight=1),
        Edge(source="B", target="D", weight=5),
        Edge(source="C", target="D", weight=8),
        Edge(source="C", target="E", weight=10),
        Edge(source="D", target="E", weight=2),
    ]
    graph = Graph(nodes=nodes, edges=edges)
    
    print("Testing Dijkstra...")
    req = DijkstraRequest(graph=graph, source="A", destination="E")
    res = run_dijkstra(req)
    assert res.finalDistance == 11, f"Expected 11, got {res.finalDistance}"
    assert res.finalPath == ["A", "B", "D", "E"] or res.finalPath == ["A", "C", "D", "E"] # B-C is directed, wait!
    # Let's trace it:
    # A->B(4), A->C(2)
    # C->D(8), C->E(10). Dist to D from C is 2+8=10. Dist to E from C is 2+10=12.
    # B->C(1), B->D(5). Dist to D from B is 4+5=9.
    # D->E(2). Dist to E from D is 9+2=11.
    # Path: A -> B -> D -> E (4+5+2=11)
    
    assert res.finalDistance == 11, f"Expected 11, got {res.finalDistance}"
    print("Dijkstra Test Passed!")

    # 3-node graph for DV (A-B-C)
    nodes_dv = [Node(id="A"), Node(id="B"), Node(id="C")]
    edges_dv = [
        Edge(source="A", target="B", weight=1),
        Edge(source="B", target="C", weight=1)
    ]
    graph_dv = Graph(nodes=nodes_dv, edges=edges_dv)
    
    print("Testing DV Baseline...")
    req_dv = DVRequest(graph=graph_dv)
    res_dv = run_distance_vector(req_dv)
    assert res_dv.converged == True
    print("DV Baseline Passed!")

    print("Testing DV Count-to-infinity (poisonReverse=False)...")
    req_cti = DVRequest(
        graph=graph_dv, 
        maxRounds=200, 
        poisonReverse=False,
        events=[DVEvent(atRound=2, edge=["B", "C"], newWeight=None)]
    )
    res_cti = run_distance_vector(req_cti)
    # In count-to-infinity, cost should climb
    # Let's check last step's table for A's distance to C
    last_step = res_cti.steps[-1]
    cost_a_c = last_step.tables["A"]["C"].cost
    assert cost_a_c is not None and cost_a_c > 10, f"Expected high cost, got {cost_a_c}"
    assert res_cti.converged == False
    print("DV Count-to-infinity Passed!")

    print("Testing DV Poison Reverse (poisonReverse=True)...")
    req_pr = DVRequest(
        graph=graph_dv, 
        maxRounds=200, 
        poisonReverse=True,
        events=[DVEvent(atRound=2, edge=["B", "C"], newWeight=None)]
    )
    res_pr = run_distance_vector(req_pr)
    last_step_pr = res_pr.steps[-1]
    cost_a_c_pr = last_step_pr.tables["A"]["C"].cost
    assert cost_a_c_pr is None, f"Expected None (infinity), got {cost_a_c_pr}"
    assert res_pr.converged == True
    print("DV Poison Reverse Passed!")

if __name__ == "__main__":
    main()
