from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import DijkstraRequest, DijkstraResponse, DVRequest, DVResponse
from algorithms.dijkstra import run_dijkstra
from algorithms.distance_vector import run_distance_vector

app = FastAPI(title="Routing Algorithm Visualizer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/dijkstra", response_model=DijkstraResponse)
def dijkstra_endpoint(request: DijkstraRequest):
    node_ids = {n.id for n in request.graph.nodes}
    
    if request.source not in node_ids:
        raise HTTPException(status_code=400, detail=f"Source node {request.source} not in graph")
        
    for edge in request.graph.edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            raise HTTPException(status_code=400, detail=f"Edge references unknown node: {edge.source}->{edge.target}")
            
    return run_dijkstra(request)

@app.post("/api/distance-vector", response_model=DVResponse)
def distance_vector_endpoint(request: DVRequest):
    node_ids = {n.id for n in request.graph.nodes}
    
    for edge in request.graph.edges:
        if edge.source not in node_ids or edge.target not in node_ids:
            raise HTTPException(status_code=400, detail=f"Edge references unknown node: {edge.source}->{edge.target}")
            
    for ev in request.events:
        for node in ev.edge:
            if node not in node_ids:
                raise HTTPException(status_code=400, detail=f"Event references unknown node: {node}")
                
    return run_distance_vector(request)
