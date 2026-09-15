"""
GridGuard Network Representation & Graph Data Structures
"""

import json
import copy
from typing import Dict, List, Optional, Any, Set


class Node:
    """Represents a facility or node in the energy grid."""
    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        supply: float = 0.0,
        demand: float = 0.0,
        enabled: bool = True,
        location: str = ""
    ):
        self.id = id
        self.name = name
        self.type = type  # 'supplier', 'transmission', 'distribution', 'destination'
        self.supply = float(supply)
        self.demand = float(demand)
        self.enabled = enabled
        self.location = location

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "supply": self.supply,
            "demand": self.demand,
            "enabled": self.enabled,
            "location": self.location
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Node":
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            supply=data.get("supply", 0.0),
            demand=data.get("demand", 0.0),
            enabled=data.get("enabled", True),
            location=data.get("location", "")
        )


class Edge:
    """Represents a transmission or distribution line in the grid."""
    def __init__(
        self,
        from_node: str,
        to_node: str,
        capacity: float,
        cost: float,
        delay: float = 1.0,
        enabled: bool = True
    ):
        self.from_node = from_node
        self.to_node = to_node
        self.capacity = float(capacity)
        self.cost = float(cost)
        self.delay = float(delay)
        self.enabled = enabled

    def to_dict(self) -> Dict[str, Any]:
        return {
            "from": self.from_node,
            "to": self.to_node,
            "capacity": self.capacity,
            "cost": self.cost,
            "delay": self.delay,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Edge":
        return cls(
            from_node=data.get("from") or data.get("from_node"),
            to_node=data.get("to") or data.get("to_node"),
            capacity=data.get("capacity", 0.0),
            cost=data.get("cost", 0.0),
            delay=data.get("delay", 1.0),
            enabled=data.get("enabled", True)
        )


class EnergyNetwork:
    """Directed graph representing the entire energy grid topology."""
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self._adj: Dict[str, List[Edge]] = {}
        self._rev_adj: Dict[str, List[Edge]] = {}

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node
        if node.id not in self._adj:
            self._adj[node.id] = []
        if node.id not in self._rev_adj:
            self._rev_adj[node.id] = []

    def add_edge(self, edge: Edge) -> None:
        self.edges.append(edge)
        if edge.from_node not in self._adj:
            self._adj[edge.from_node] = []
        self._adj[edge.from_node].append(edge)

        if edge.to_node not in self._rev_adj:
            self._rev_adj[edge.to_node] = []
        self._rev_adj[edge.to_node].append(edge)

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.nodes.get(node_id)

    def get_edge(self, u: str, v: str) -> Optional[Edge]:
        for edge in self._adj.get(u, []):
            if edge.to_node == v:
                return edge
        return None

    def get_suppliers(self, only_enabled: bool = False) -> List[Node]:
        return [
            n for n in self.nodes.values()
            if n.type == "supplier" and (not only_enabled or n.enabled)
        ]

    def get_destinations(self, only_enabled: bool = False) -> List[Node]:
        return [
            n for n in self.nodes.values()
            if n.type == "destination" and (not only_enabled or n.enabled)
        ]

    def get_outgoing_edges(self, node_id: str, only_enabled: bool = True) -> List[Edge]:
        edges = self._adj.get(node_id, [])
        if not only_enabled:
            return edges
        return [e for e in edges if e.enabled and self.nodes.get(e.to_node, Node("", "", "", enabled=False)).enabled]

    def get_incoming_edges(self, node_id: str, only_enabled: bool = True) -> List[Edge]:
        edges = self._rev_adj.get(node_id, [])
        if not only_enabled:
            return edges
        return [e for e in edges if e.enabled and self.nodes.get(e.from_node, Node("", "", "", enabled=False)).enabled]

    def disable_node(self, node_id: str) -> bool:
        if node_id in self.nodes:
            self.nodes[node_id].enabled = False
            return True
        return False

    def enable_node(self, node_id: str) -> bool:
        if node_id in self.nodes:
            self.nodes[node_id].enabled = True
            return True
        return False

    def reset_all(self) -> None:
        for node in self.nodes.values():
            node.enabled = True
        for edge in self.edges:
            edge.enabled = True

    def clone(self) -> "EnergyNetwork":
        """Returns an independent deep copy of the network."""
        cloned = EnergyNetwork()
        for node in self.nodes.values():
            cloned.add_node(Node.from_dict(node.to_dict()))
        for edge in self.edges:
            cloned.add_edge(Edge.from_dict(edge.to_dict()))
        return cloned

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EnergyNetwork":
        net = cls()
        for n_data in data.get("nodes", []):
            net.add_node(Node.from_dict(n_data))
        for e_data in data.get("edges", []):
            net.add_edge(Edge.from_dict(e_data))
        return net

    @classmethod
    def load_from_file(cls, filepath: str) -> "EnergyNetwork":
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
