"""
GridGuard REST API & Web Server Entrypoint
Provides REST endpoints for network queries, disruption simulation, and static UI serving.
Compatible with standard WSGI servers and Vercel Serverless Python runtime.
"""

import os
import sys
import json
from flask import Flask, jsonify, request, send_from_directory

# Ensure backend modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.network import EnergyNetwork
from backend.simulation import run_disruption_simulation

# Locate data and frontend paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "network.json")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


# Load master network graph
def load_grid_network() -> EnergyNetwork:
    if os.path.exists(DATA_PATH):
        return EnergyNetwork.load_from_file(DATA_PATH)
    raise FileNotFoundError(f"Network data file not found at {DATA_PATH}")


# Predefined Demo Scenarios
DEMO_SCENARIOS = [
    {
        "id": "scenario-1",
        "title": "Scenario 1: Major Supplier Failure",
        "node_id": "P1",
        "node_name": "North Thermal Plant",
        "description": "Disable the largest supplier (150 MW). Simulates how BFS detects disrupted downstream nodes (S1, S4, D1) and Dijkstra reroutes energy from Central Hydro (P2) and South Nuclear (P3).",
        "expected_effect": "Cascade along North corridor; capacity-constrained alternative reroutes to Metro City and Industrial Zone."
    },
    {
        "id": "scenario-2",
        "title": "Scenario 2: Central Transmission Failure",
        "node_id": "S2",
        "node_name": "Central Switching Station",
        "description": "Disable the central transmission backbone (S2). Demonstrates multi-substation rerouting via East (S3) and South (S5) corridors under bottleneck limits.",
        "expected_effect": "Core switching disrupted; tests peripheral bypass circuits and evaluates additional transmission delays."
    },
    {
        "id": "scenario-3",
        "title": "Scenario 3: South Bulk Substation Outage",
        "node_id": "S5",
        "node_name": "South Bulk Substation",
        "description": "Disable South Substation (S5), cutting direct connection from South Nuclear (P3) to Port Logistics (D4) and Harbor Port (C4).",
        "expected_effect": "Harbor Port must draw alternate power from North/Central plants via multi-hop distribution hubs."
    }
]


# CORS support for API endpoints
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Static Frontend Routing
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(FRONTEND_DIR, path)):
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


# API Endpoints
@app.route("/api/network", methods=["GET"])
def get_network():
    """Returns the complete base network topology."""
    try:
        network = load_grid_network()
        return jsonify({
            "success": True,
            "data": network.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Failed to load network topology: {str(e)}"
        }), 500


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """
    Executes disruption simulation on a target disabled node.
    Request body: { "disabled_node": "P1" }
    """
    try:
        data = request.get_json(force=True, silent=True) or {}
        disabled_node_id = data.get("disabled_node")

        if not disabled_node_id:
            return jsonify({
                "error": True,
                "message": "Missing required field 'disabled_node' in request body."
            }), 400

        network = load_grid_network()
        if disabled_node_id not in network.nodes:
            return jsonify({
                "error": True,
                "message": f"Node '{disabled_node_id}' does not exist in network."
            }), 404

        simulation_result = run_disruption_simulation(network, disabled_node_id)
        return jsonify({
            "success": True,
            "simulation": simulation_result
        }), 200

    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Simulation execution error: {str(e)}"
        }), 500


@app.route("/api/reset", methods=["POST"])
def reset_network():
    """Resets the network to its nominal healthy state."""
    try:
        network = load_grid_network()
        network.reset_all()
        return jsonify({
            "success": True,
            "message": "Network successfully reset to nominal operational state.",
            "data": network.to_dict()
        }), 200
    except Exception as e:
        return jsonify({
            "error": True,
            "message": f"Failed to reset network: {str(e)}"
        }), 500


@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    """Returns predefined resilience test scenarios."""
    return jsonify({
        "success": True,
        "scenarios": DEMO_SCENARIOS
    }), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] GridGuard Server starting on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
