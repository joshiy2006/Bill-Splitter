import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Routing Algorithm Visualizer</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0f172a;
      --panel: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --accent: #10b981;
      --danger: #ef4444;
      --border: #334155;
      
      --node-bg: #334155;
      --node-border: #94a3b8;
      --node-visited: #10b981;
      --node-current: #3b82f6;
      --edge-color: #64748b;
      --edge-highlight: #f59e0b;
      --font: 'Inter', sans-serif;
    }
    
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: var(--font); background: var(--bg); color: var(--text); min-height: 100vh; overflow-x: hidden; }
    
    .container { max-width: 1400px; margin: 0 auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; height: 100vh; }
    
    .header { text-align: center; padding: 20px 0; border-bottom: 1px solid var(--border); }
    .header h1 { font-size: 28px; font-weight: 700; background: linear-gradient(to right, #3b82f6, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    
    .tabs { display: flex; justify-content: center; gap: 10px; margin-top: 15px; }
    .tab { padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: 0.2s; border: 1px solid var(--border); background: var(--panel); color: var(--text-muted); }
    .tab.active { background: var(--primary); color: white; border-color: var(--primary); box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4); }
    
    .main-grid { display: grid; grid-template-columns: 300px 1fr 350px; gap: 20px; flex: 1; min-height: 0; }
    
    .panel { background: var(--panel); border: 1px solid var(--border); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 15px; overflow-y: auto; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.3); }
    .panel h2 { font-size: 18px; margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
    
    .btn { background: var(--primary); color: white; border: none; padding: 10px 15px; border-radius: 6px; cursor: pointer; font-weight: 500; transition: 0.2s; font-family: var(--font); display: inline-flex; align-items: center; justify-content: center; gap: 8px;}
    .btn:hover { background: var(--primary-hover); }
    .btn.outline { background: transparent; border: 1px solid var(--primary); color: var(--primary); }
    .btn.outline:hover { background: rgba(59, 130, 246, 0.1); }
    .btn.danger { background: var(--danger); border: 1px solid var(--danger); color: white;}
    .btn.danger:hover { background: #dc2626; }
    .btn:disabled { opacity: 0.5; cursor: not-allowed; }
    
    .input-group { display: flex; flex-direction: column; gap: 5px; }
    .input-group label { font-size: 14px; color: var(--text-muted); }
    .input-group input, .input-group select { background: var(--bg); border: 1px solid var(--border); color: var(--text); padding: 8px; border-radius: 6px; font-family: var(--font); outline: none; }
    .input-group input:focus, .input-group select:focus { border-color: var(--primary); }
    
    .svg-container { flex: 1; background: var(--panel); border: 1px solid var(--border); border-radius: 12px; position: relative; overflow: hidden; box-shadow: inset 0 2px 10px rgba(0,0,0,0.2);}
    svg { width: 100%; height: 100%; cursor: crosshair; }
    .node { cursor: pointer; transition: 0.2s; }
    .node circle { fill: var(--node-bg); stroke: var(--node-border); stroke-width: 3; transition: 0.3s; }
    .node.visited circle { fill: var(--node-visited); stroke: #059669; }
    .node.current circle { fill: var(--node-current); stroke: #2563eb; }
    .node.broadcasting circle { fill: var(--edge-highlight); stroke: #d97706; }
    .node text { fill: white; font-weight: 600; font-size: 14px; pointer-events: none; }
    
    .edge line { stroke: var(--edge-color); stroke-width: 3; transition: 0.3s; }
    .edge.highlight line { stroke: var(--edge-highlight); stroke-width: 5; }
    .edge.directed { marker-end: url(#arrowhead); }
    .edge text { fill: var(--text); font-size: 14px; font-weight: bold; paint-order: stroke; stroke: var(--bg); stroke-width: 4px; pointer-events: none; }
    
    .controls { display: flex; align-items: center; justify-content: space-between; padding: 15px; background: rgba(30,41,59,0.9); backdrop-filter: blur(8px); border-radius: 12px; border: 1px solid var(--border); position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 600px; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.5);}
    
    .step-slider { flex: 1; margin: 0 20px; }
    .step-slider input[type="range"] { width: 100%; accent-color: var(--primary); }
    
    .table-container { font-size: 14px; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; }
    th, td { padding: 8px; text-align: left; border-bottom: 1px solid var(--border); }
    th { color: var(--text-muted); font-weight: 500; }
    .changed { background: rgba(245, 158, 11, 0.2); animation: flash 1s ease; }
    
    @keyframes flash { 0% { background: rgba(245, 158, 11, 0.8); } 100% { background: rgba(245, 158, 11, 0.2); } }
    
    .toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 15px; }
    .mode-btn { flex: 1; min-width: 80px; }
    .mode-btn.active { background: var(--primary); color: white; border-color: var(--primary); }
    
    .error-box { background: rgba(239, 68, 68, 0.1); border: 1px solid var(--danger); color: #fca5a5; padding: 12px; border-radius: 8px; font-size: 14px; margin-bottom: 15px; }
  </style>
</head>
<body>
  <div id="root"></div>

  <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
  <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
  <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>

  <script type="text/babel">
    const { useState, useEffect, useRef, useMemo, useCallback } = React;
    const API_BASE = 'http://127.0.0.1:8000/api';

    // --- Graph Helpers ---
    const generateId = () => Math.random().toString(36).substr(2, 6).toUpperCase();
    
    const generateRandomGraph = () => {
      const numNodes = 5;
      const nodes = Array.from({length: numNodes}, (_, i) => ({
        id: String.fromCharCode(65 + i),
        x: 100 + Math.random() * 400,
        y: 100 + Math.random() * 300
      }));
      const edges = [];
      for(let i = 0; i < numNodes; i++) {
        for(let j = i+1; j < numNodes; j++) {
          if (Math.random() > 0.4) { // 60% chance of edge
            edges.push({
              id: generateId(),
              source: nodes[i].id,
              target: nodes[j].id,
              weight: Math.floor(Math.random() * 10) + 1
            });
          }
        }
      }
      return { nodes, edges };
    };

    // --- Hooks ---
    function useDijkstra(graph) {
      const [steps, setSteps] = useState([]);
      const [loading, setLoading] = useState(false);
      const [error, setError] = useState(null);
      
      const run = async (source, destination) => {
        setLoading(true); setError(null);
        try {
          const res = await fetch(`${API_BASE}/dijkstra`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ graph, source, destination: destination || null })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || 'API Error');
          setSteps(data.steps);
        } catch(e) { setError(e.message); setSteps([]); }
        finally { setLoading(false); }
      };
      
      return { steps, loading, error, run, setSteps };
    }

    function useDistanceVector(graph) {
      const [result, setResult] = useState(null);
      const [loading, setLoading] = useState(false);
      const [error, setError] = useState(null);
      
      const run = async (maxRounds, poisonReverse, events) => {
        setLoading(true); setError(null);
        try {
          const res = await fetch(`${API_BASE}/distance-vector`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ graph, maxRounds, poisonReverse, events })
          });
          const data = await res.json();
          if (!res.ok) throw new Error(data.detail || 'API Error');
          setResult(data);
        } catch(e) { setError(e.message); setResult(null); }
        finally { setLoading(false); }
      };
      
      return { steps: result?.steps || [], result, loading, error, run, setResult };
    }

    // --- Components ---
    const GraphSVG = ({ nodes, edges, activeTab, stepData, onCanvasClick, onNodeClick, mode, edgeStart }) => {
      // stepData is the current step for the active algorithm
      
      const getNodeClass = (nodeId) => {
        let cls = "node";
        if (activeTab === 'dijkstra' && stepData) {
          if (stepData.currentNode === nodeId) cls += " current";
          else if (stepData.visited?.includes(nodeId)) cls += " visited";
        } else if (activeTab === 'dv' && stepData) {
          if (stepData.broadcastingNode === nodeId) cls += " broadcasting";
        }
        if (edgeStart === nodeId) cls += " current"; // highlight selected node for edge
        return cls;
      };

      const isEdgeHighlighted = (e) => {
        if (!stepData) return false;
        if (activeTab === 'dijkstra') {
          return stepData.relaxedEdges?.some(re => 
            (re.source === e.source && re.target === e.target) || 
            (re.source === e.target && re.target === e.source)
          );
        } else if (activeTab === 'dv') {
          // If we had a direct broadcast animation, we could highlight it
          return false;
        }
        return false;
      };

      return (
        <div className="svg-container" onClick={onCanvasClick}>
          <svg>
            <defs>
              <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="25" refY="3.5" orient="auto">
                <polygon points="0 0, 10 3.5, 0 7" fill="var(--edge-color)" />
              </marker>
            </defs>
            {/* Draw Edges */}
            {edges.map(e => {
              const n1 = nodes.find(n => n.id === e.source);
              const n2 = nodes.find(n => n.id === e.target);
              if(!n1 || !n2) return null;
              
              const midX = (n1.x + n2.x) / 2;
              const midY = (n1.y + n2.y) / 2;
              
              return (
                <g key={e.id} className={`edge ${isEdgeHighlighted(e) ? 'highlight' : ''}`}>
                  <line x1={n1.x} y1={n1.y} x2={n2.x} y2={n2.y} />
                  <rect x={midX - 10} y={midY - 10} width="20" height="20" fill="var(--bg)" rx="4"/>
                  <text x={midX} y={midY} textAnchor="middle" dominantBaseline="central">{e.weight}</text>
                </g>
              );
            })}
            
            {/* Draw Preview Edge */}
            {mode === 'addEdge' && edgeStart && (
              <g className="edge">
                {/* Needs cursor tracking for actual line, skipped for simplicity, just highlight start node */}
              </g>
            )}

            {/* Draw Nodes */}
            {nodes.map(n => (
              <g key={n.id} className={getNodeClass(n.id)} transform={`translate(${n.x}, ${n.y})`} 
                 onClick={(ev) => { ev.stopPropagation(); onNodeClick(n); }}>
                <circle r="20" />
                <text textAnchor="middle" dominantBaseline="central">{n.id}</text>
              </g>
            ))}
          </svg>
        </div>
      );
    };

    const StepPlayer = ({ steps, currentStepIdx, setCurrentStepIdx }) => {
      const [isPlaying, setIsPlaying] = useState(false);
      const [speed, setSpeed] = useState(1000);
      const timerRef = useRef(null);

      const stepData = steps[currentStepIdx];
      const maxIdx = Math.max(0, steps.length - 1);

      useEffect(() => {
        if (isPlaying && currentStepIdx < maxIdx) {
          timerRef.current = setTimeout(() => {
            setCurrentStepIdx(c => c + 1);
          }, speed);
        } else if (isPlaying && currentStepIdx >= maxIdx) {
          setIsPlaying(false);
        }
        return () => clearTimeout(timerRef.current);
      }, [isPlaying, currentStepIdx, speed, maxIdx]);

      const handlePlayPause = () => setIsPlaying(!isPlaying);
      const handlePrev = () => { setIsPlaying(false); setCurrentStepIdx(c => Math.max(0, c - 1)); }
      const handleNext = () => { setIsPlaying(false); setCurrentStepIdx(c => Math.min(maxIdx, c + 1)); }

      if (steps.length === 0) return null;

      return (
        <div className="controls">
          <button className="btn outline" onClick={handlePrev} disabled={currentStepIdx === 0}>◀ Step</button>
          <button className="btn" onClick={handlePlayPause}>{isPlaying ? '⏸ Pause' : '▶ Play'}</button>
          <button className="btn outline" onClick={handleNext} disabled={currentStepIdx === maxIdx}>Step ▶</button>
          
          <div className="step-slider">
            <input type="range" min="0" max={maxIdx} value={currentStepIdx} 
                   onChange={(e) => {setIsPlaying(false); setCurrentStepIdx(parseInt(e.target.value));}} />
            <div style={{textAlign: 'center', marginTop: '5px', fontSize: '12px', color: 'var(--text-muted)'}}>
              Step {currentStepIdx} / {maxIdx} <br/>
              {stepData?.description}
            </div>
          </div>
          
          <div className="input-group" style={{width: '80px'}}>
            <select value={speed} onChange={(e) => setSpeed(parseInt(e.target.value))}>
              <option value={2000}>Slow</option>
              <option value={1000}>Normal</option>
              <option value={500}>Fast</option>
            </select>
          </div>
        </div>
      );
    };

    const App = () => {
      const [activeTab, setActiveTab] = useState('dijkstra');
      const [nodes, setNodes] = useState([]);
      const [edges, setEdges] = useState([]);
      const [mode, setMode] = useState('select'); // 'select', 'addNode', 'addEdge', 'remove'
      const [edgeStart, setEdgeStart] = useState(null);
      const [nodeIdCounter, setNodeIdCounter] = useState(65); // ASCII 'A'
      
      const { steps: dSteps, loading: dLoading, error: dError, run: runD, setSteps: setDSteps } = useDijkstra({nodes, edges});
      const { steps: dvSteps, result: dvResult, loading: dvLoading, error: dvError, run: runDV, setResult: setDVResult } = useDistanceVector({nodes, edges});
      
      const [dStepIdx, setDStepIdx] = useState(0);
      const [dvStepIdx, setDVStepIdx] = useState(0);

      // Dijkstra controls
      const [dSource, setDSource] = useState('');
      const [dDest, setDDest] = useState('');

      // DV controls
      const [dvRounds, setDvRounds] = useState(200);
      const [dvPoison, setDvPoison] = useState(false);
      const [dvEvents, setDvEvents] = useState([]); // [{atRound, u, v, weight}]

      useEffect(() => {
        const g = generateRandomGraph();
        setNodes(g.nodes);
        setEdges(g.edges);
        setNodeIdCounter(65 + g.nodes.length);
      }, []);
      
      const clearSteps = () => {
        setDSteps([]); setDStepIdx(0);
        setDVResult(null); setDVStepIdx(0);
      };

      const handleCanvasClick = (e) => {
        if (mode === 'addNode') {
          const rect = e.target.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          const id = String.fromCharCode(nodeIdCounter);
          setNodes([...nodes, { id, x, y }]);
          setNodeIdCounter(c => c + 1);
          clearSteps();
        }
        setEdgeStart(null);
      };

      const handleNodeClick = (n) => {
        if (mode === 'remove') {
          setNodes(nodes.filter(node => node.id !== n.id));
          setEdges(edges.filter(e => e.source !== n.id && e.target !== n.id));
          clearSteps();
        } else if (mode === 'addEdge') {
          if (!edgeStart) {
            setEdgeStart(n.id);
          } else {
            if (n.id !== edgeStart) {
              const exists = edges.some(e => (e.source === edgeStart && e.target === n.id) || (e.source === n.id && e.target === edgeStart));
              if (!exists) {
                const weight = parseInt(prompt("Enter edge weight (positive integer):", "1") || "1");
                if (weight > 0) {
                  setEdges([...edges, { id: generateId(), source: edgeStart, target: n.id, weight }]);
                  clearSteps();
                }
              }
            }
            setEdgeStart(null);
          }
        }
      };

      const handleRunDijkstra = () => {
        setDStepIdx(0);
        runD(dSource || nodes[0]?.id, dDest || null);
      };

      const handleRunDV = () => {
        setDVStepIdx(0);
        const formattedEvents = dvEvents.map(ev => ({
          atRound: ev.atRound,
          edge: [ev.u, ev.v],
          newWeight: ev.weight === 'failed' ? null : parseInt(ev.weight)
        }));
        runDV(dvRounds, dvPoison, formattedEvents);
      };
      
      const addEvent = () => {
        setDvEvents([...dvEvents, { atRound: 2, u: nodes[0]?.id || '', v: nodes[1]?.id || '', weight: 'failed' }]);
      };

      const currentSteps = activeTab === 'dijkstra' ? dSteps : dvSteps;
      const currentStepIdx = activeTab === 'dijkstra' ? dStepIdx : dvStepIdx;
      const stepData = currentSteps[currentStepIdx];
      const error = activeTab === 'dijkstra' ? dError : dvError;

      return (
        <div className="container">
          <div className="header">
            <h1>Routing Algorithm Visualizer</h1>
            <div className="tabs">
              <div className={`tab ${activeTab === 'dijkstra' ? 'active' : ''}`} onClick={() => setActiveTab('dijkstra')}>Dijkstra's Algorithm</div>
              <div className={`tab ${activeTab === 'dv' ? 'active' : ''}`} onClick={() => setActiveTab('dv')}>Distance Vector</div>
            </div>
          </div>
          
          <div className="main-grid">
            <div className="panel">
              <h2>Graph Builder</h2>
              <div className="toolbar">
                <button className={`btn outline mode-btn ${mode === 'select' ? 'active' : ''}`} onClick={() => setMode('select')}>Select</button>
                <button className={`btn outline mode-btn ${mode === 'addNode' ? 'active' : ''}`} onClick={() => setMode('addNode')}>+ Node</button>
                <button className={`btn outline mode-btn ${mode === 'addEdge' ? 'active' : ''}`} onClick={() => setMode('addEdge')}>+ Edge</button>
                <button className={`btn outline mode-btn ${mode === 'remove' ? 'active' : ''}`} onClick={() => setMode('remove')}>🗑 Remove</button>
              </div>
              <button className="btn" onClick={() => {
                const g = generateRandomGraph();
                setNodes(g.nodes); setEdges(g.edges); setNodeIdCounter(65 + g.nodes.length); clearSteps();
              }}>🎲 Random Graph</button>
              <button className="btn danger" onClick={() => { setNodes([]); setEdges([]); setNodeIdCounter(65); clearSteps(); }}>Clear All</button>
              
              <hr style={{borderColor: 'var(--border)'}}/>
              
              {activeTab === 'dijkstra' && (
                <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
                  <h2>Dijkstra Settings</h2>
                  <div className="input-group">
                    <label>Source Node</label>
                    <select value={dSource} onChange={e => setDSource(e.target.value)}>
                      {nodes.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
                    </select>
                  </div>
                  <div className="input-group">
                    <label>Destination Node (Optional)</label>
                    <select value={dDest} onChange={e => setDDest(e.target.value)}>
                      <option value="">None (All pairs)</option>
                      {nodes.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
                    </select>
                  </div>
                  <button className="btn" onClick={handleRunDijkstra} disabled={dLoading || nodes.length===0}>
                    {dLoading ? 'Computing...' : 'Run Dijkstra'}
                  </button>
                </div>
              )}
              
              {activeTab === 'dv' && (
                <div style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
                  <h2>Distance Vector Settings</h2>
                  <div className="input-group" style={{flexDirection: 'row', alignItems: 'center', gap: '10px'}}>
                    <input type="checkbox" id="poison" checked={dvPoison} onChange={e => setDvPoison(e.target.checked)}/>
                    <label htmlFor="poison">Enable Poison Reverse</label>
                  </div>
                  <div className="input-group">
                    <label>Max Rounds</label>
                    <input type="number" value={dvRounds} onChange={e => setDvRounds(parseInt(e.target.value))} min="1" max="200" />
                  </div>
                  
                  <h4>Scheduled Events</h4>
                  {dvEvents.map((ev, i) => (
                    <div key={i} style={{background: 'var(--bg)', padding: '10px', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '5px'}}>
                      <div style={{display: 'flex', gap: '5px'}}>
                        <input style={{width:'50px'}} type="number" value={ev.atRound} onChange={e => {const n = [...dvEvents]; n[i].atRound = parseInt(e.target.value); setDvEvents(n);}}/>
                        <select value={ev.u} onChange={e => {const n = [...dvEvents]; n[i].u = e.target.value; setDvEvents(n);}}>
                           {nodes.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
                        </select>
                        <span>-</span>
                        <select value={ev.v} onChange={e => {const n = [...dvEvents]; n[i].v = e.target.value; setDvEvents(n);}}>
                           {nodes.map(n => <option key={n.id} value={n.id}>{n.id}</option>)}
                        </select>
                      </div>
                      <div style={{display: 'flex', gap: '5px'}}>
                        <input style={{flex: 1}} type="text" placeholder="Weight or 'failed'" value={ev.weight} onChange={e => {const n = [...dvEvents]; n[i].weight = e.target.value; setDvEvents(n);}}/>
                        <button className="btn danger" style={{padding: '5px'}} onClick={() => setDvEvents(dvEvents.filter((_, idx) => idx !== i))}>X</button>
                      </div>
                    </div>
                  ))}
                  <button className="btn outline" onClick={addEvent}>+ Add Event</button>
                  
                  <button className="btn" onClick={handleRunDV} disabled={dvLoading || nodes.length===0}>
                    {dvLoading ? 'Simulating...' : 'Simulate DV'}
                  </button>
                </div>
              )}
            </div>
            
            <div style={{position: 'relative', display: 'flex', flexDirection: 'column'}}>
              {error && <div className="error-box">{error}</div>}
              <GraphSVG nodes={nodes} edges={edges} activeTab={activeTab} stepData={stepData} 
                        onCanvasClick={handleCanvasClick} onNodeClick={handleNodeClick} 
                        mode={mode} edgeStart={edgeStart} />
              
              <StepPlayer steps={currentSteps} currentStepIdx={currentStepIdx} 
                          setCurrentStepIdx={activeTab === 'dijkstra' ? setDStepIdx : setDVStepIdx} />
            </div>
            
            <div className="panel table-container">
              <h2>State Tables</h2>
              
              {activeTab === 'dijkstra' && stepData && (
                <div>
                  <p style={{color:'var(--text-muted)', marginBottom: '10px'}}>
                    <strong>Current Node:</strong> {stepData.currentNode || 'None'}<br/>
                    <strong>Visited:</strong> {stepData.visited.join(', ') || 'None'}
                  </p>
                  <table>
                    <thead>
                      <tr>
                        <th>Node</th>
                        <th>Distance</th>
                        <th>Prev</th>
                      </tr>
                    </thead>
                    <tbody>
                      {nodes.map(n => (
                        <tr key={n.id} className={stepData.currentNode === n.id ? 'changed' : ''}>
                          <td>{n.id}</td>
                          <td>{stepData.distances[n.id] === null ? '∞' : stepData.distances[n.id]}</td>
                          <td>{stepData.predecessors[n.id] || '-'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {activeTab === 'dv' && stepData && (
                <div>
                  <p style={{color:'var(--text-muted)', marginBottom: '10px'}}>
                    <strong>Round:</strong> {stepData.round} <br/>
                    {dvResult && currentStepIdx === currentSteps.length - 1 && (
                      <strong style={{color: dvResult.converged ? 'var(--accent)' : 'var(--danger)'}}>
                        {dvResult.converged ? 'Converged!' : 'Did not converge (Max Rounds)'}
                      </strong>
                    )}
                  </p>
                  
                  {nodes.map(n => {
                    const t = stepData.tables[n.id];
                    if (!t) return null;
                    return (
                      <div key={n.id} style={{marginBottom: '15px'}}>
                        <h4 style={{marginBottom: '5px', color: 'var(--primary)'}}>Router {n.id}</h4>
                        <table>
                          <thead>
                            <tr>
                              <th>Dest</th>
                              <th>Cost</th>
                              <th>Next Hop</th>
                            </tr>
                          </thead>
                          <tbody>
                            {nodes.map(d => {
                              const entry = t[d.id];
                              if (!entry) return null;
                              const changed = stepData.changedEntries.some(ce => ce.node === n.id && ce.dest === d.id);
                              return (
                                <tr key={d.id} className={changed ? 'changed' : ''}>
                                  <td>{d.id}</td>
                                  <td>{entry.cost === null ? '∞' : entry.cost}</td>
                                  <td>{entry.nextHop || '-'}</td>
                                </tr>
                              );
                            })}
                          </tbody>
                        </table>
                      </div>
                    );
                  })}
                </div>
              )}
              
              {(!stepData || currentSteps.length === 0) && (
                <div style={{color: 'var(--text-muted)', textAlign: 'center', marginTop: '40px'}}>
                  Run an algorithm to see tables here.
                </div>
              )}
            </div>
          </div>
        </div>
      );
    };

    const root = ReactDOM.createRoot(document.getElementById('root'));
    root.render(<App />);
  </script>
</body>
</html>
"""

with open(r"c:\Users\HP\OneDrive\Desktop\CN assignment\frontend\index.html", "w", encoding="utf-8") as f:
    f.write(html_content)
