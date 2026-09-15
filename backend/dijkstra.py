"""
GridGuard Dijkstra Algorithm with Min-Heap Priority Queue
Calculates lowest-cost paths, transmission latencies, and bottleneck capacities.
"""

from typing import Dict, List, Optional, Tuple, Any, Set
from .network import EnergyNetwork, Edge
from .heap import MinHeap


def find_shortest_path(
    network: EnergyNetwork,
    start_node_id: str,
    target_node_id: str,
    excluded_edges: Optional[Set[Tuple[str, str]]] = None
) -> Optional[Dict[str, Any]]:
    """
    Finds the lowest-cost path from start_node_id to target_node_id using
    Dijkstra's algorithm with a custom Min-Heap priority queue.
    
    Complexity: O((V + E) log V) where V is the number of grid nodes and E is transmission lines.
    """
    if excluded_edges is None:
        excluded_edges = set()

    start_node = network.get_node(start_node_id)
    target_node = network.get_node(target_node_id)

    if not start_node or not target_node:
        return None
    if not start_node.enabled or not target_node.enabled:
        return None

    # Min-Heap stores (cost_so_far, node_id)
    heap = MinHeap()
    heap.push(0.0, start_node_id)

    # Tracking lowest cost and path reconstruction
    min_costs: Dict[str, float] = {start_node_id: 0.0}
    delays_map: Dict[str, float] = {start_node_id: 0.0}
    previous: Dict[str, Optional[str]] = {start_node_id: None}
    visited: Set[str] = set()

    while not heap.is_empty():
        current_cost, current_node_id = heap.pop()

        if current_node_id in visited:
            continue
        visited.add(current_node_id)

        # Early exit if target is reached with optimal cost
        if current_node_id == target_node_id:
            break

        current_delay = delays_map.get(current_node_id, 0.0)

        # Explore outgoing edges
        for edge in network.get_outgoing_edges(current_node_id, only_enabled=True):
            neighbor_id = edge.to_node

            # Check if edge is explicitly excluded (e.g. for finding alternative routes)
            if (edge.from_node, edge.to_node) in excluded_edges:
                continue

            # Ensure neighbor node is enabled
            neighbor_node = network.get_node(neighbor_id)
            if not neighbor_node or not neighbor_node.enabled:
                continue

            new_cost = current_cost + edge.cost
            new_delay = current_delay + edge.delay

            if neighbor_id not in min_costs or new_cost < min_costs[neighbor_id]:
                min_costs[neighbor_id] = new_cost
                delays_map[neighbor_id] = new_delay
                previous[neighbor_id] = current_node_id
                heap.push(new_cost, neighbor_id)

    # If target was not reached
    if target_node_id not in min_costs or target_node_id not in previous:
        return None

    # Reconstruct path sequence from target back to start
    path: List[str] = []
    curr: Optional[str] = target_node_id
    while curr is not None:
        path.append(curr)
        curr = previous.get(curr)
    path.reverse()

    # If path doesn't start at start_node_id, target is unreachable
    if not path or path[0] != start_node_id:
        return None

    # Calculate bottleneck capacity and collect edge details along the path
    path_edges: List[Dict[str, Any]] = []
    bottleneck_capacity = float("inf")
    total_cost = 0.0
    total_delay = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge = network.get_edge(u, v)
        if edge:
            path_edges.append(edge.to_dict())
            bottleneck_capacity = min(bottleneck_capacity, edge.capacity)
            total_cost += edge.cost
            total_delay += edge.delay

    if bottleneck_capacity == float("inf"):
        bottleneck_capacity = 0.0

    return {
        "source": start_node_id,
        "destination": target_node_id,
        "path": path,
        "path_str": " → ".join(path),
        "total_cost": total_cost,
        "total_delay": total_delay,
        "bottleneck_capacity": bottleneck_capacity,
        "edges": path_edges,
        "hops": len(path) - 1
    }


def find_all_paths_dijkstra(
    network: EnergyNetwork,
    start_node_id: str,
    target_node_id: str,
    max_routes: int = 3
) -> List[Dict[str, Any]]:
    """
    Finds top k diverse alternative paths from start to target using iterative
    penalty / edge exclusion variations of Dijkstra's algorithm.
    """
    routes: List[Dict[str, Any]] = []
    excluded_edges: Set[Tuple[str, str]] = set()

    for _ in range(max_routes):
        route = find_shortest_path(network, start_node_id, target_node_id, excluded_edges)
        if not route:
            break
        
        routes.append(route)
        
        # To find alternative route, exclude the bottleneck or critical middle edge
        path = route["path"]
        if len(path) > 2:
            # Exclude an intermediate edge
            excluded_edges.add((path[1], path[2]))
        elif len(path) == 2:
            excluded_edges.add((path[0], path[1]))
        else:
            break

    return routes
