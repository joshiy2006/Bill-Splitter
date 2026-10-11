from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class Node(BaseModel):
    id: str
    x: float = 0.0
    y: float = 0.0

class Edge(BaseModel):
    source: str
    target: str
    weight: float

class Graph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

class DijkstraRequest(BaseModel):
    graph: Graph
    source: str
    destination: Optional[str] = None

class DijkstraStep(BaseModel):
    stepIndex: int
    currentNode: Optional[str]
    visited: List[str]
    distances: Dict[str, Optional[float]] # None means infinity
    predecessors: Dict[str, Optional[str]]
    relaxedEdges: List[Dict[str, str]] # [{'source': 'A', 'target': 'B'}]
    description: str

class DijkstraResponse(BaseModel):
    steps: List[DijkstraStep]
    finalPath: Optional[List[str]] = None
    finalDistance: Optional[float] = None

class DVEvent(BaseModel):
    atRound: int
    edge: List[str] # [nodeA, nodeB]
    newWeight: Optional[float] = None # None means link failure

class DVRequest(BaseModel):
    graph: Graph
    maxRounds: int = Field(default=200, ge=1, le=200)
    poisonReverse: bool = False
    events: List[DVEvent] = []

class DVTableEntry(BaseModel):
    cost: Optional[float] = None # None means infinity
    nextHop: Optional[str] = None

class DVStep(BaseModel):
    stepIndex: int
    round: int
    broadcastingNode: Optional[str]
    tables: Dict[str, Dict[str, DVTableEntry]] # node -> dest -> entry
    changedEntries: List[Dict[str, str]] # [{'node': 'A', 'dest': 'C'}]
    event: Optional[str] = None
    description: str

class DVResponse(BaseModel):
    steps: List[DVStep]
    converged: bool
    roundsRun: int
