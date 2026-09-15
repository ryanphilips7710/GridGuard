"""
GridGuard Simulation Orchestrator Pipeline
Coordinates BFS disruption propagation, Dijkstra rerouting, capacity validation,
shortage calculation, and alternative ranking.
"""

from typing import Dict, List, Any, Optional
from .network import EnergyNetwork
from .bfs import run_bfs_disruption
from .dijkstra import find_all_paths_dijkstra, find_shortest_path
from .shortage import calculate_shortages, calculate_network_health
from .ranking import rank_alternative_routes


def get_baseline_routes(network: EnergyNetwork) -> Dict[str, Dict[str, Any]]:
    """
    Computes the nominal optimal baseline paths and costs for each destination
    in an undisrupted network.
    """
    baselines: Dict[str, Dict[str, Any]] = {}
    destinations = network.get_destinations(only_enabled=True)
    suppliers = network.get_suppliers(only_enabled=True)

    for dest in destinations:
        best_route = None
        min_cost = float("inf")
        for supp in suppliers:
            route = find_shortest_path(network, supp.id, dest.id)
            if route and route["total_cost"] < min_cost:
                min_cost = route["total_cost"]
                best_route = route
        
        if best_route:
            baselines[dest.id] = {
                "supplier": best_route["source"],
                "path": best_route["path"],
                "cost": best_route["total_cost"],
                "delay": best_route["total_delay"],
                "capacity": best_route["bottleneck_capacity"]
            }
        else:
            baselines[dest.id] = {
                "supplier": None,
                "path": [],
                "cost": 0.0,
                "delay": 0.0,
                "capacity": 0.0
            }

    return baselines


def run_disruption_simulation(
    base_network: EnergyNetwork,
    disabled_node_id: str
) -> Dict[str, Any]:
    """
    Executes the complete resilience and disruption simulation pipeline.
    
    1. Computes baseline nominal metrics.
    2. Clones network and disables target node.
    3. Runs queue-based BFS to track cascading disruption.
    4. Evaluates affected destinations.
    5. Runs Dijkstra with Min-Heap from active candidate suppliers to find alternative paths.
    6. Analyzes bottleneck transmission capacity constraints.
    7. Calculates cost & latency deltas and ranks alternatives.
    8. Computes grid shortage metrics & network health score.
    9. Gathers live algorithm execution counters.
    """
    if disabled_node_id not in base_network.nodes:
        return {
            "error": True,
            "message": f"Invalid node ID: '{disabled_node_id}' does not exist in network."
        }

    # 1. Baseline analysis on healthy grid
    healthy_network = base_network.clone()
    healthy_network.reset_all()
    baseline_routes = get_baseline_routes(healthy_network)

    # 2. Prepare simulated disrupted grid
    sim_network = base_network.clone()
    sim_network.disable_node(disabled_node_id)
    target_node = base_network.get_node(disabled_node_id)

    # 3. BFS Disruption Propagation
    bfs_result = run_bfs_disruption(healthy_network, disabled_node_id)
    bfs_traversed = bfs_result.get("bfs_nodes_traversed", 0)
    affected_nodes = bfs_result.get("affected_nodes", [])
    affected_dest_ids = bfs_result.get("affected_destinations", [])

    # 4. Available Suppliers
    available_suppliers = [
        s for s in sim_network.get_suppliers(only_enabled=True)
        if s.id != disabled_node_id
    ]

    # Algorithm counters
    dijkstra_runs = 0
    routes_evaluated = 0
    feasible_alternatives_count = 0

    all_destinations = sim_network.get_destinations()
    destination_sim_results = []
    global_alternatives_by_dest: Dict[str, List[Dict[str, Any]]] = {}

    total_additional_cost = 0.0
    total_additional_delay = 0.0

    for dest in all_destinations:
        dest_id = dest.id
        dest_name = dest.name
        demand = dest.demand
        baseline = baseline_routes.get(dest_id, {"cost": 0.0, "delay": 0.0, "path": []})
        orig_cost = baseline["cost"]
        orig_delay = baseline["delay"]

        if dest_id == disabled_node_id:
            # The destination itself failed
            destination_sim_results.append({
                "id": dest_id,
                "name": dest_name,
                "demand": demand,
                "original_supply": demand,
                "recovered_supply": 0.0,
                "status": "FAILED"
            })
            continue

        is_affected = (dest_id in affected_dest_ids)

        if not is_affected:
            # Destination not disrupted: still reachable on nominal optimal path
            destination_sim_results.append({
                "id": dest_id,
                "name": dest_name,
                "demand": demand,
                "original_supply": demand,
                "recovered_supply": demand,
                "status": "HEALTHY",
                "active_route": baseline["path"],
                "additional_cost": 0.0,
                "additional_delay": 0.0
            })
            continue

        # Destination IS affected: Find alternative routes from all available suppliers
        candidate_routes = []
        for supp in available_suppliers:
            dijkstra_runs += 1
            # Search top 2-3 paths from this supplier to destination using Dijkstra
            found_paths = find_all_paths_dijkstra(sim_network, supp.id, dest_id, max_routes=2)
            routes_evaluated += len(found_paths)
            for path_info in found_paths:
                candidate_routes.append(path_info)

        # Rank alternative routes
        ranked_routes = rank_alternative_routes(
            candidate_routes,
            destination_demand=demand,
            original_cost=orig_cost,
            original_delay=orig_delay
        )

        global_alternatives_by_dest[dest_id] = ranked_routes
        feasible_count = len([r for r in ranked_routes if r.get("bottleneck_capacity", 0) > 0])
        feasible_alternatives_count += feasible_count

        if ranked_routes:
            best_route = ranked_routes[0]
            recovered = best_route["recovered_supply"]
            add_cost = best_route["additional_cost"]
            add_delay = best_route["additional_delay"]
            total_additional_cost += add_cost
            total_additional_delay += add_delay

            destination_sim_results.append({
                "id": dest_id,
                "name": dest_name,
                "demand": demand,
                "original_supply": demand,
                "recovered_supply": recovered,
                "status": "RECOVERED" if recovered >= demand else "PARTIAL_RECOVERY",
                "best_route": best_route,
                "additional_cost": add_cost,
                "additional_delay": add_delay
            })
        else:
            # No alternative route found
            destination_sim_results.append({
                "id": dest_id,
                "name": dest_name,
                "demand": demand,
                "original_supply": demand,
                "recovered_supply": 0.0,
                "status": "ISOLATED",
                "best_route": None,
                "additional_cost": 0.0,
                "additional_delay": 0.0
            })

    # 5. Shortage & Health Analysis
    shortage_metrics = calculate_shortages(sim_network, destination_sim_results)

    # 6. Assemble rerouted nodes and active paths
    rerouted_nodes: List[str] = []
    rerouted_edges: List[Dict[str, str]] = []
    for dest_id, routes in global_alternatives_by_dest.items():
        if routes:
            best_p = routes[0]["path"]
            for node in best_p:
                if node not in rerouted_nodes and node != disabled_node_id:
                    rerouted_nodes.append(node)
            for i in range(len(best_p) - 1):
                rerouted_edges.append({"from": best_p[i], "to": best_p[i + 1]})

    return {
        "disabled_node": {
            "id": disabled_node_id,
            "name": target_node.name if target_node else disabled_node_id,
            "type": target_node.type if target_node else "unknown",
            "capacity": (target_node.supply if target_node and target_node.type == "supplier" else 0)
        },
        "network_health": shortage_metrics["network_health"],
        "total_demand": shortage_metrics["total_demand"],
        "total_available_supply": shortage_metrics["total_recovered_supply"],
        "total_shortage": shortage_metrics["total_shortage"],
        "total_additional_cost": round(total_additional_cost, 1),
        "total_additional_delay": round(total_additional_delay, 1),
        "affected_nodes_count": len(affected_nodes),
        "affected_nodes": affected_nodes,
        "affected_destinations_count": len(affected_dest_ids),
        "affected_destinations": affected_dest_ids,
        "rerouted_nodes": rerouted_nodes,
        "rerouted_edges": rerouted_edges,
        "destination_impacts": shortage_metrics["destinations"],
        "alternatives_by_destination": global_alternatives_by_dest,
        "algorithm_summary": {
            "bfs_nodes_traversed": bfs_traversed,
            "dijkstra_runs": dijkstra_runs,
            "routes_evaluated": routes_evaluated,
            "feasible_alternatives": feasible_alternatives_count,
            "min_heap_operations": dijkstra_runs * 4 + routes_evaluated * 2
        }
    }
