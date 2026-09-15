"""
GridGuard BFS Disruption Propagation Algorithm
Queue-based Breadth-First Search for cascading disruption tracking.
"""

from collections import deque
from typing import Dict, List, Set, Tuple, Any
from .network import EnergyNetwork


def run_bfs_disruption(
    network: EnergyNetwork,
    disabled_node_id: str
) -> Dict[str, Any]:
    """
    Simulates disruption propagation across the grid using a queue-based BFS.
    
    1. Traverses downstream from the disabled node to find all potentially impacted nodes.
    2. Runs reachability checks from remaining active suppliers to identify which
       destinations become isolated or lose critical power flow.
    3. Returns detailed disruption metrics, affected nodes, and destination impacts.
    
    Complexity: O(V + E) where V is the number of grid nodes and E is the number of transmission lines.
    """
    if disabled_node_id not in network.nodes:
        return {
            "error": True,
            "message": f"Node {disabled_node_id} not found in grid."
        }

    # Step 1: Traverse downstream from the failed node using standard queue BFS
    queue: deque = deque([disabled_node_id])
    visited: Set[str] = {disabled_node_id}
    traversal_order: List[str] = []
    downstream_nodes: List[str] = []
    propagation_edges: List[Dict[str, str]] = []

    nodes_traversed_count = 0

    while queue:
        current = queue.popleft()
        nodes_traversed_count += 1
        traversal_order.append(current)

        for edge in network.get_outgoing_edges(current, only_enabled=False):
            neighbor = edge.to_node
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
                downstream_nodes.append(neighbor)
                propagation_edges.append({"from": current, "to": neighbor})

    # Step 2: Determine global reachability from all REMAINING active suppliers
    # Active suppliers (excluding disabled_node_id)
    active_suppliers = [
        s.id for s in network.get_suppliers(only_enabled=True)
        if s.id != disabled_node_id
    ]

    reachable_from_active_suppliers: Set[str] = set()
    supplier_queue = deque(active_suppliers)
    for s_id in active_suppliers:
        reachable_from_active_suppliers.add(s_id)

    while supplier_queue:
        curr = supplier_queue.popleft()
        nodes_traversed_count += 1
        for edge in network.get_outgoing_edges(curr, only_enabled=True):
            nxt = edge.to_node
            # Cannot traverse through disabled node
            if nxt == disabled_node_id:
                continue
            if nxt not in reachable_from_active_suppliers:
                reachable_from_active_suppliers.add(nxt)
                supplier_queue.append(nxt)

    # Step 3: Identify affected destinations
    # Destinations are affected if:
    # a) They were in the downstream blast radius of the disabled node, OR
    # b) They are no longer fully reachable without rerouting, OR
    # c) If the disabled node was a supplier or critical transmission node feeding them.
    all_destinations = [d.id for d in network.get_destinations()]
    affected_destinations: List[str] = []
    isolated_destinations: List[str] = []

    for dest_id in all_destinations:
        if dest_id == disabled_node_id:
            affected_destinations.append(dest_id)
            isolated_destinations.append(dest_id)
        elif dest_id not in reachable_from_active_suppliers:
            # Completely disconnected from active suppliers
            affected_destinations.append(dest_id)
            isolated_destinations.append(dest_id)
        elif dest_id in downstream_nodes:
            # Downstream of disabled node, lost primary feed path and requires verification/reroute
            affected_destinations.append(dest_id)

    # Affected nodes in the grid (excluding suppliers that remain operational)
    affected_nodes = [
        node_id for node_id in downstream_nodes
        if node_id != disabled_node_id and network.nodes[node_id].type != "supplier"
    ]

    return {
        "disabled_node": disabled_node_id,
        "bfs_nodes_traversed": nodes_traversed_count,
        "traversal_order": traversal_order,
        "downstream_nodes": downstream_nodes,
        "propagation_edges": propagation_edges,
        "affected_nodes": affected_nodes,
        "affected_destinations": affected_destinations,
        "isolated_destinations": isolated_destinations,
        "reachable_from_active_suppliers": list(reachable_from_active_suppliers),
        "active_suppliers_count": len(active_suppliers)
    }
