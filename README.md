# GridGuard — Energy Network Resilience & Disruption Simulator

> **Simulate • Detect • Reroute • Recover**  
> An interactive algorithmic resilience simulator modeling energy transmission disruptions, cascading failure propagation via BFS, and minimum-cost capacity-constrained alternative rerouting using Dijkstra with a Binary Min-Heap (`heapq`).

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-3.28%2B-orange.svg)](https://js.cytoscape.org/)
[![Vercel](https://img.shields.io/badge/Vercel-Serverless%20Ready-black.svg)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ⚡ 1. Problem & Solution Overview

### The Problem
Modern power grids are complex, interconnected graph networks. When a high-voltage substation, switching hub, or power plant fails (due to equipment malfunction, extreme weather, or physical damage), disruptions cascade downstream. Grid operators must rapidly:
1. Identify all downstream substations and cities that lose direct supply.
2. Calculate the resulting energy shortage in Megawatts (MW).
3. Discover viable alternative supply routes from active power plants.
4. Enforce transmission line capacity constraints (preventing secondary line overloads).
5. Quantify financial costs ($\Delta \text{Cost}$) and transmission latency ($\Delta \text{Delay}$) to rank optimal recovery routes.

### The Solution: GridGuard
**GridGuard** is an interactive, full-stack energy resilience dashboard powered by authentic computer science graph algorithms:
- **BFS (Breadth-First Search)** traverses the directed grid to trace the exact blast radius and reachability loss from failed nodes.
- **Dijkstra's Algorithm with a custom Min-Heap Priority Queue (`heapq`)** discovers the lowest-cost alternative supply routes.
- **Bottleneck Capacity Analysis** ensures rerouted lines do not exceed physical megawatt thresholds:
  $$\text{Path Capacity} = \min_{e \in \text{Path}} (\text{Capacity}(e))$$
- **Multi-Factor Route Ranking Engine** scores and ranks candidate paths with transparent explanations.
- **Interactive Cytoscape.js Mesh** visualizes failure states, affected corridors, and animated recovery paths in real-time.

---

## 🏗️ 2. System Architecture & Algorithms

```
[ USER INTERFACE / DASHBOARD ]
  │
  ├── Cytoscape.js Topology Mesh (16 Nodes • 31 Directed Edges)
  ├── Live Health Index Ring & Impact Dashboard
  └── Ranked Alternative Route Visualizer
        │
        ▼  (REST API: /api/simulate)
[ FLASK ORCHESTRATION PIPELINE (backend/simulation.py) ]
  │
  ├── 1. BFS Disruption Engine (backend/bfs.py)
  │      └── Queue-based cascading reachability analysis
  │
  ├── 2. Shortage Engine (backend/shortage.py)
  │      └── Evaluates demand vs pre-failure / post-failure supply
  │
  ├── 3. Dijkstra Rerouting Engine (backend/dijkstra.py)
  │      └── Min-Heap Priority Queue (backend/heap.py + heapq)
  │
  ├── 4. Capacity & Bottleneck Engine
  │      └── Enforces transmission line MW throughput limits
  │
  └── 5. Multi-Criteria Route Ranking (backend/ranking.py)
         └── Computes cost deltas, latency penalties, and shortage deficits
```

---

## 📊 3. Core Algorithms & Time Complexity

| Algorithm | Implementation File | Role in GridGuard | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- | :--- |
| **Breadth-First Search (BFS)** | [`backend/bfs.py`](file:///c:/Users/HOME/Downloads/GridGuard/backend/bfs.py) | Traces disruption propagation downstream from disabled facility | $\mathcal{O}(V + E)$ | $\mathcal{O}(V)$ |
| **Dijkstra Shortest Path** | [`backend/dijkstra.py`](file:///c:/Users/HOME/Downloads/GridGuard/backend/dijkstra.py) | Finds lowest-cost alternative transmission routes | $\mathcal{O}((V + E) \log V)$ | $\mathcal{O}(V)$ |
| **Binary Min-Heap** | [`backend/heap.py`](file:///c:/Users/HOME/Downloads/GridGuard/backend/heap.py) | Priority queue powering Dijkstra with `heapq` | $\mathcal{O}(\log N)$ per op | $\mathcal{O}(N)$ |
| **Bottleneck Capacity** | [`backend/shortage.py`](file:///c:/Users/HOME/Downloads/GridGuard/backend/shortage.py) | Computes min edge capacity along path | $\mathcal{O}(L)$ where $L = \text{hops}$ | $\mathcal{O}(1)$ |
| **Multi-Criteria Ranking** | [`backend/ranking.py`](file:///c:/Users/HOME/Downloads/GridGuard/backend/ranking.py) | Evaluates composite penalty score: $\Delta \text{Cost} + \Delta \text{Delay} + \text{Shortage}$ | $\mathcal{O}(K \log K)$ | $\mathcal{O}(K)$ |

Where:
- $V = \text{Total Nodes (16 facilities: 3 Power Plants, 5 Substations, 4 Distribution Hubs, 4 Cities)}$
- $E = \text{Total Transmission Lines (31 directed edges)}$
- $K = \text{Candidate alternative routes evaluated per destination}$

---

## 📁 4. Project Structure

```text
GridGuard/
│
├── api/
│   └── index.py               # Flask REST server & Vercel WSGI entrypoint
│
├── backend/
│   ├── __init__.py            # Backend package exports
│   ├── network.py             # Graph data structures (Node, Edge, EnergyNetwork)
│   ├── bfs.py                 # Queue-based BFS disruption propagation algorithm
│   ├── heap.py                # Min-Heap Priority Queue wrapper around Python heapq
│   ├── dijkstra.py            # Manual Dijkstra algorithm with bottleneck checking
│   ├── shortage.py            # Shortage calculations & Grid Health Index formula
│   ├── ranking.py             # Multi-factor alternative route ranking engine
│   └── simulation.py          # Master simulation pipeline orchestrator
│
├── data/
│   └── network.json           # 16-node energy mesh with capacities, costs, latencies
│
├── frontend/
│   ├── index.html             # Modern command center dashboard layout
│   ├── style.css              # Cyber-grid dark theme with neon accents & glassmorphism
│   ├── graph.js               # Cytoscape.js interactive topology manager & animations
│   └── app.js                 # Frontend application controller & REST API client
│
├── test_simulation.py         # Complete automated test suite (13 unit/integration tests)
├── requirements.txt           # Python dependencies (Flask, Flask-CORS)
├── vercel.json                # Vercel serverless deployment config
└── README.md                  # Comprehensive project documentation
```

---

## 🚀 5. Getting Started (Local Setup)

### Prerequisites
- Python 3.10+ installed
- Modern Web Browser (Chrome, Firefox, Edge, Safari)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/GridGuard.git
cd GridGuard
pip install -r requirements.txt
```

### 2. Run Automated Test Suite
Verify that all 13 algorithm and integration tests pass:
```bash
python test_simulation.py
```
Expected output:
```text
.............
----------------------------------------------------------------------
Ran 13 tests in 0.083s

OK
```

### 3. Launch the Local Development Server
```bash
python api/index.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## 🌐 6. Deployment on Vercel

GridGuard is structured for instant one-click deployment on **Vercel Serverless Functions**:

1. Install the Vercel CLI or link via GitHub:
   ```bash
   npm i -g vercel
   vercel
   ```
2. The included [`vercel.json`](file:///c:/Users/HOME/Downloads/GridGuard/vercel.json) automatically directs incoming requests to [`api/index.py`](file:///c:/Users/HOME/Downloads/GridGuard/api/index.py) using the `@vercel/python` builder.
3. Static files are served directly from the [`frontend/`](file:///c:/Users/HOME/Downloads/GridGuard/frontend) directory.

---

## 📡 7. REST API Reference

### `GET /api/network`
Returns the complete baseline grid topology.
- **Response:**
  ```json
  {
    "success": true,
    "data": {
      "nodes": [{ "id": "P1", "name": "North Thermal Plant", "type": "supplier", "supply": 150, "demand": 0, "enabled": true }],
      "edges": [{ "from": "P1", "to": "S1", "capacity": 110, "cost": 5, "delay": 1, "enabled": true }]
    }
  }
  ```

---

### `POST /api/simulate`
Executes disruption simulation on a target disabled facility.
- **Request Body:**
  ```json
  {
    "disabled_node": "P1"
  }
  ```
- **Response Body:**
  ```json
  {
    "success": true,
    "simulation": {
      "disabled_node": { "id": "P1", "name": "North Thermal Plant", "type": "supplier", "capacity": 150 },
      "network_health": 94,
      "total_demand": 250.0,
      "total_available_supply": 235.0,
      "total_shortage": 15.0,
      "total_additional_cost": 23.0,
      "total_additional_delay": 2.0,
      "affected_nodes_count": 12,
      "affected_nodes": ["S1", "S4", "S2", "D1", "S3", "D2", "D4", "C1", "C3", "D3", "C2", "C4"],
      "affected_destinations_count": 4,
      "destination_impacts": [
        {
          "destination": "C1",
          "name": "Metro City Capital",
          "demand": 80.0,
          "original_supply": 80.0,
          "recovered_supply": 65.0,
          "remaining_shortage": 15.0,
          "coverage": 81.2
        }
      ],
      "alternatives_by_destination": {
        "C1": [
          {
            "rank": 1,
            "is_best": true,
            "path": ["P2", "S2", "D1", "C1"],
            "path_str": "P2 → S2 → D1 → C1",
            "total_cost": 21.0,
            "total_delay": 4.0,
            "bottleneck_capacity": 65.0,
            "additional_cost": 5.0,
            "additional_delay": 1.0,
            "recovered_supply": 65.0,
            "remaining_shortage": 15.0,
            "coverage": 81.2,
            "score": 11.9,
            "rank_explanation": "15.0 MW deficit due to 65.0 MW bottleneck; +₹5.0 cost delta; +1.0h delay"
          }
        ]
      },
      "algorithm_summary": {
        "bfs_nodes_traversed": 27,
        "dijkstra_runs": 8,
        "routes_evaluated": 16,
        "feasible_alternatives": 12,
        "min_heap_operations": 64
      }
    }
  }
  ```

---

### `POST /api/reset`
Restores all facilities and transmission lines back to operational baseline.

---

### `GET /api/scenarios`
Returns predefined hackathon demonstration scenarios.

---

## 🔬 8. Interactive Demo Scenarios

### Scenario 1: Major Power Plant Failure (P1 — North Thermal Plant)
- **Action:** Disables the 150 MW North Power Plant.
- **Cascade:** BFS propagates through North Substation (S1), West Substation (S4), and Metro Distribution (D1).
- **Reroute:** Central Hydro Plant (P2) and South Nuclear Plant (P3) reroute power through Central Switching Station (S2) to Metro City (C1).
- **Bottleneck Analysis:** Rerouted line S2 $\rightarrow$ D1 has a 65 MW limit against an 80 MW demand, leaving a 15 MW shortage clearly surfaced by the algorithm.

### Scenario 2: Backbone Switching Station Failure (S2 — Central Switching)
- **Action:** Disables the core central interconnect.
- **Cascade:** Isolates primary east-west transmission links.
- **Reroute:** Energy is diverted through peripheral circuits (S5 South Bulk and S3 East Hub), incurring quantifiable additional transmission delay (+2.0h) and cost (+₹45).

---

## 🛡️ 9. Code Quality & Standards

- **Zero Blackbox Optimization Libraries:** BFS, Dijkstra, Min-Heap, Shortage, and Ranking engines are written in pure Python using `collections.deque` and `heapq`.
- **Clean Separation of Concerns:** Algorithm logic is isolated in `backend/`, API routing in `api/index.py`, and UI controls in `frontend/`.
- **Dynamic Calculation:** Every metric, node count, Dijkstra run, and route cost is calculated dynamically on-the-fly.

---

## 📜 License
MIT License. Created for College & Hackathon Demonstrations.
