# ⚡ GridGuard — Energy Network Resilience & Disruption Simulator

> **Simulate • Detect • Reroute • Recover**

An interactive energy network resilience simulator that models transmission disruptions, cascading failures, energy shortages, and intelligent alternative routing using **BFS, Dijkstra's Algorithm, and a Binary Min-Heap**.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![Cytoscape.js](https://img.shields.io/badge/Cytoscape.js-3.28%2B-orange.svg)](https://js.cytoscape.org/)
[![Vercel](https://img.shields.io/badge/Vercel-Serverless%20Ready-black.svg)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Live Demo

**[Launch GridGuard →](https://gridguard-livid.vercel.app/)**

> Interactive deployment of the GridGuard energy resilience simulator.

---

## 📸 Dashboard Preview

<img width="959" height="495" alt="image" src="https://github.com/user-attachments/assets/e5708ecb-6143-45fa-b34c-ba59f0a86309" />


---

# ⚡ 1. Problem & Solution

## The Problem

Modern energy grids are complex, interconnected graph networks. When a power plant, high-voltage substation, switching hub, or transmission facility fails due to equipment malfunction, extreme weather, or physical damage, the disruption can propagate through connected infrastructure.

Grid operators need to rapidly:

1. Identify affected downstream facilities and destinations.
2. Calculate the resulting energy shortage in Megawatts (MW).
3. Discover viable alternative supply routes.
4. Ensure alternative transmission lines do not exceed their capacity.
5. Quantify additional routing cost.
6. Quantify additional transmission delay.
7. Rank the available recovery options.

## The Solution

**GridGuard** models the energy infrastructure as a directed weighted graph and uses classical graph algorithms to simulate network disruptions and recovery.

### BFS — Disruption Propagation

**Breadth-First Search** traverses the network from a failed facility to determine affected downstream nodes and reachability loss.

### Dijkstra + Min-Heap — Alternative Routing

**Dijkstra's Algorithm**, powered by a binary Min-Heap using Python's `heapq`, identifies low-cost alternative supply routes from active suppliers to affected destinations.

### Capacity Analysis

Every transmission line has a maximum capacity.

For a candidate route:

```text
Path Capacity = minimum edge capacity along the route
```

This ensures that an alternative route cannot supply more energy than its bottleneck transmission line can physically carry.

### Route Ranking

Candidate routes are evaluated using factors such as:

* Additional cost
* Additional delay
* Available capacity
* Remaining shortage

The resulting alternatives are ranked and presented to the user.

---

## ✨ Key Features

* 🕸️ **Interactive Energy Network** — Visualize a 16-node, 31-edge directed energy transmission network.
* ⚠️ **Disruption Simulation** — Disable power plants, substations, or other facilities and simulate their impact.
* 🔎 **BFS Disruption Propagation** — Identify affected nodes and downstream network reachability.
* 🧭 **Dijkstra Alternative Routing** — Find minimum-cost alternative supply paths.
* ⚡ **Binary Min-Heap** — Efficient priority queue powering Dijkstra's algorithm.
* 📊 **Capacity-Aware Routing** — Prevent alternative routes from exceeding transmission capacity.
* 📉 **Shortage Analysis** — Calculate unmet energy demand in MW.
* 💰 **Additional Cost Analysis** — Quantify the cost difference caused by rerouting.
* ⏱️ **Delay Analysis** — Calculate additional transmission latency.
* 🏆 **Route Ranking** — Rank feasible alternatives using transparent scoring.
* ❤️ **Network Health Index** — Measure overall grid integrity after disruption.
* 🎬 **Demo Scenarios** — Predefined disruption scenarios for quick demonstrations.
* 🔄 **Network Recovery Visualization** — Visually distinguish failed, affected, and rerouted portions of the grid.
* 🌐 **Vercel Deployment** — Serverless-ready Flask backend with an interactive web frontend.

---

# 🏗️ 2. System Architecture

```text
┌───────────────────────────────────────────────┐
│                GRIDGUARD UI                   │
│                                               │
│ HTML + CSS + JavaScript + Cytoscape.js        │
│                                               │
│ • Interactive Topology Mesh                   │
│ • Node Inspector                              │
│ • Network Health Index                        │
│ • Impact Dashboard                            │
│ • Alternative Route Ranking                   │
└───────────────────────┬───────────────────────┘
                        │
                        │ REST API
                        ▼
┌───────────────────────────────────────────────┐
│              FLASK API LAYER                  │
│                                               │
│ /api/network                                  │
│ /api/simulate                                 │
│ /api/reset                                    │
│ /api/scenarios                                │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│           SIMULATION ENGINE                   │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ BFS Disruption Engine                     │ │
│ │ → Cascading reachability analysis         │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ Shortage Engine                           │ │
│ │ → Demand vs available supply              │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ Dijkstra Routing Engine                   │ │
│ │ → Minimum-cost alternative paths          │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ Capacity Analysis                         │ │
│ │ → Bottleneck transmission constraints     │ │
│ └───────────────────────────────────────────┘ │
│                                               │
│ ┌───────────────────────────────────────────┐ │
│ │ Route Ranking Engine                      │ │
│ │ → Cost + delay + shortage evaluation      │ │
│ └───────────────────────────────────────────┘ │
└───────────────────────────────────────────────┘
```

---

# 🧠 4. Core Algorithms

| Algorithm               | Purpose                                 | Time Complexity          | Space Complexity |
| ----------------------- | --------------------------------------- | ------------------------ | ---------------- |
| **BFS**                 | Disruption propagation and reachability | `O(V + E)`               | `O(V)`           |
| **Dijkstra**            | Minimum-cost alternative routing        | `O((V + E) log V)`       | `O(V)`           |
| **Binary Min-Heap**     | Priority queue for Dijkstra             | `O(log N)` per operation | `O(N)`           |
| **Bottleneck Capacity** | Determines route capacity               | `O(L)`                   | `O(1)`           |
| **Route Ranking**       | Ranks candidate recovery routes         | `O(K log K)`             | `O(K)`           |

Where:

* `V` = number of nodes
* `E` = number of directed transmission edges
* `L` = number of hops in a route
* `K` = number of candidate routes

### Network Size

The default GridGuard network contains:

```text
16 Nodes
31 Directed Transmission Lines

3 Power Plants
5 Substations
4 Distribution Hubs
4 Destinations
```

---

# 🛠️ 5. Technology Stack

| Layer               | Technology              |
| ------------------- | ----------------------- |
| Frontend            | HTML5, CSS3, JavaScript |
| Graph Visualization | Cytoscape.js            |
| Backend             | Python                  |
| Web Framework       | Flask                   |
| Graph Algorithms    | BFS, Dijkstra           |
| Priority Queue      | Python `heapq`          |
| Data Storage        | JSON                    |
| API                 | REST                    |
| Deployment          | Vercel                  |
| Version Control     | Git / GitHub            |

---

# 📁 6. Project Structure

```text
GridGuard/
│
├── api/
│   └── index.py               # Flask REST server & Vercel entrypoint
│
├── backend/
│   ├── __init__.py            # Backend package
│   ├── network.py             # Graph data structures
│   ├── bfs.py                 # BFS disruption propagation
│   ├── heap.py                # Min-Heap wrapper using heapq
│   ├── dijkstra.py            # Dijkstra routing algorithm
│   ├── shortage.py            # Shortage & health calculations
│   ├── ranking.py             # Alternative route ranking
│   └── simulation.py          # Master simulation pipeline
│
├── data/
│   └── network.json           # 16-node energy network
│
├── frontend/
│   ├── index.html             # Dashboard UI
│   ├── style.css              # Dashboard styling
│   ├── graph.js               # Cytoscape.js graph manager
│   └── app.js                 # Frontend controller & API client
│
├── docs/
│   └── dashboard.png          # Project screenshot
│
├── test_simulation.py         # Automated test suite
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel deployment configuration
└── README.md                  # Project documentation
```

---

# 🚀 7. Getting Started

## Prerequisites

* Python 3.10+
* Git
* Modern web browser
* Internet connection for Cytoscape.js CDN

## Clone the Repository

```bash
git clone https://github.com/ryanphilips7710/GridGuard.git
cd GridGuard
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Tests

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

## Start the Development Server

```bash
python api/index.py
```

Then open:

```text
http://localhost:5000
```

---

# 📡 8. REST API

## `GET /api/network`

Returns the complete baseline network topology.

Example:

```json
{
  "success": true,
  "data": {
    "nodes": [
      {
        "id": "P1",
        "name": "North Thermal Plant",
        "type": "supplier",
        "supply": 150,
        "demand": 0,
        "enabled": true
      }
    ],
    "edges": [
      {
        "from": "P1",
        "to": "S1",
        "capacity": 110,
        "cost": 5,
        "delay": 1,
        "enabled": true
      }
    ]
  }
}
```

---

## `POST /api/simulate`

Executes a disruption simulation.

### Request

```json
{
  "disabled_node": "P1"
}
```

### Response

```json
{
  "success": true,
  "simulation": {
    "disabled_node": "P1",
    "network_health": 94,
    "total_demand": 250.0,
    "total_available_supply": 235.0,
    "total_shortage": 15.0,
    "total_additional_cost": 23.0,
    "total_additional_delay": 2.0,
    "affected_nodes_count": 12,
    "affected_destinations_count": 4
  }
}
```

The simulation response also includes destination-level impact, alternative routes, route rankings, and algorithm execution statistics.

---

## `POST /api/reset`

Restores the network to its nominal operational state.

---

## `GET /api/scenarios`

Returns predefined demonstration scenarios.

---

# 🔮 9. Future Improvements

Potential future extensions include:

* Larger dynamically generated networks
* Real-world energy grid datasets
* Multiple simultaneous node failures
* Advanced flow optimization
* Max-Flow / Min-Cut analysis
* Real-time energy demand changes
* Weather-driven disruption scenarios
* Historical disruption replay
* User-created network configurations
* Real-time monitoring dashboards
* More advanced resilience scoring

---

Python • Flask • JavaScript • Cytoscape.js • BFS • Dijkstra • Min-Heap • Vercel
