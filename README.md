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

| Algorithm               | Implementation                               | Purpose                                 | Time Complexity          | Space Complexity |
| ----------------------- | -------------------------------------------- | --------------------------------------- | ------------------------ | ---------------- |
| **BFS**                 | [`backend/bfs.py`](backend/bfs.py)           | Disruption propagation and reachability | `O(V + E)`               | `O(V)`           |
| **Dijkstra**            | [`backend/dijkstra.py`](backend/dijkstra.py) | Minimum-cost alternative routing        | `O((V + E) log V)`       | `O(V)`           |
| **Binary Min-Heap**     | [`backend/heap.py`](backend/heap.py)         | Priority queue for Dijkstra             | `O(log N)` per operation | `O(N)`           |
| **Bottleneck Capacity** | [`backend/shortage.py`](backend/shortage.py) | Determines route capacity               | `O(L)`                   | `O(1)`           |
| **Route Ranking**       | [`backend/ranking.py`](backend/ranking.py)   | Ranks candidate recovery routes         | `O(K log K)`             | `O(K)`           |

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

# 📡 10. REST API

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

# 📊 11. Example Simulation Output

A disruption can produce an analysis such as:

```text
NETWORK HEALTH
94%

TOTAL DEMAND
250 MW

AVAILABLE SUPPLY
235 MW

TOTAL SHORTAGE
15 MW

ADDITIONAL COST
₹23

ADDITIONAL DELAY
+2.0 hrs

AFFECTED NODES
12

AFFECTED DESTINATIONS
4
```

For an affected destination:

```text
Destination: Metro City

Demand:
80 MW

Recovered Supply:
65 MW

Remaining Shortage:
15 MW

Coverage:
81.2%

Best Alternative:
P2 → S2 → D1 → C1

Route Capacity:
65 MW

Additional Cost:
₹5

Additional Delay:
+1 hour
```

---

# 🧪 12. Testing

GridGuard includes an automated test suite covering algorithmic and integration behavior.

Tests include:

* BFS disruption propagation
* Network reachability
* Dijkstra minimum-cost routing
* Path reconstruction
* Min-Heap operations
* Capacity constraints
* Shortage calculation
* Alternative supplier selection
* Route ranking
* Simulation behavior
* Reset functionality
* API behavior
* Edge cases

Run:

```bash
python test_simulation.py
```

---

# 🌐 13. Deployment

GridGuard is structured for deployment on **Vercel**.

The Flask application is exposed through:

```text
api/index.py
```

and the Vercel configuration is defined in:

```text
vercel.json
```

## Deploy Using GitHub

1. Push the repository to GitHub.
2. Open Vercel.
3. Import the GridGuard repository.
4. Select the project root as the root directory.
5. Deploy.

## Deploy Using Vercel CLI

```bash
npm install -g vercel
```

Then:

```bash
vercel
```

The Vercel configuration routes requests through the Flask application.

### Production URL

**https://gridguard-livid.vercel.app/**

---

# 🛡️ 14. Design & Code Quality

### No Black-Box Graph Algorithms

The core graph algorithms are implemented explicitly in Python.

GridGuard does not rely on NetworkX or another graph library to perform BFS or Dijkstra.

The implementation uses:

```python
from collections import deque
```

for BFS and:

```python
import heapq
```

for the Dijkstra priority queue.

### Separation of Concerns

```text
backend/
    Algorithm & simulation logic

api/
    REST API & Flask routing

frontend/
    UI & visualization

data/
    Network configuration
```

### Dynamic Calculation

Simulation metrics are calculated dynamically from the network rather than being hard-coded.

This includes:

* Affected node count
* Shortage
* Recovered supply
* Alternative routes
* Route costs
* Delays
* Network health
* Dijkstra executions
* Candidate routes
* Min-Heap operations

---

# 🎯 15. Why GridGuard?

Traditional graph algorithm demonstrations often show a shortest-path problem in isolation.

GridGuard puts those algorithms into a practical infrastructure-resilience scenario.

Instead of simply asking:

> **"What is the shortest path?"**

GridGuard asks:

> **"What happens when part of an energy network fails, how much supply is lost, and what is the best feasible way to recover it?"**

This connects fundamental Computer Science concepts with a real-world infrastructure problem.

---

# 🔮 16. Future Improvements

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

# 📜 17. License

MIT License.

Created for college and hackathon demonstrations.

---

## 👨‍💻 Project

**GridGuard — Energy Network Resilience & Disruption Simulator**

**Repository:**
https://github.com/ryanphilips7710/GridGuard

**Live Demo:**
https://gridguard-livid.vercel.app/

**Core Technologies:**
Python • Flask • JavaScript • Cytoscape.js • BFS • Dijkstra • Min-Heap • Vercel
