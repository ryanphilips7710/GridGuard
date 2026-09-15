"""
GridGuard Comprehensive Automated Test Suite
Validates BFS, Dijkstra, Min-Heap, Capacity Analysis, Shortage Calculation, Route Ranking, and Flask API.
"""

import os
import sys
import unittest
import json

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.network import EnergyNetwork, Node, Edge
from backend.heap import MinHeap
from backend.bfs import run_bfs_disruption
from backend.dijkstra import find_shortest_path, find_all_paths_dijkstra
from backend.shortage import calculate_shortages, calculate_network_health
from backend.ranking import rank_alternative_routes
from backend.simulation import run_disruption_simulation
from api.index import app


class TestGridGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data_path = os.path.join(os.path.dirname(__file__), "data", "network.json")
        cls.network = EnergyNetwork.load_from_file(cls.data_path)
        cls.client = app.test_client()

    def test_01_network_topology_loaded(self):
        """Verify network contains 16 nodes and 31 edges with proper properties."""
        self.assertEqual(len(self.network.nodes), 16)
        self.assertEqual(len(self.network.edges), 31)

        suppliers = self.network.get_suppliers()
        destinations = self.network.get_destinations()
        self.assertEqual(len(suppliers), 3)
        self.assertEqual(len(destinations), 4)

        # Check node data integrity
        p1 = self.network.get_node("P1")
        self.assertIsNotNone(p1)
        self.assertEqual(p1.supply, 150.0)
        self.assertEqual(p1.type, "supplier")

        c1 = self.network.get_node("C1")
        self.assertIsNotNone(c1)
        self.assertEqual(c1.demand, 80.0)
        self.assertEqual(c1.type, "destination")

    def test_02_min_heap_operations(self):
        """Verify MinHeap priority queue operations using heapq."""
        heap = MinHeap()
        self.assertTrue(heap.is_empty())
        self.assertEqual(len(heap), 0)

        # Push items with various costs
        heap.push(25.0, "route_c")
        heap.push(10.0, "route_a")
        heap.push(15.0, "route_b")
        heap.push(10.0, "route_a_duplicate_cost")

        self.assertEqual(len(heap), 4)
        self.assertFalse(heap.is_empty())

        # Pop in ascending order
        p1, item1 = heap.pop()
        self.assertEqual(p1, 10.0)
        p2, item2 = heap.pop()
        self.assertEqual(p2, 10.0)
        p3, item3 = heap.pop()
        self.assertEqual(p3, 15.0)
        p4, item4 = heap.pop()
        self.assertEqual(p4, 25.0)

        self.assertTrue(heap.is_empty())

    def test_03_bfs_disruption_propagation(self):
        """Verify BFS detects disrupted nodes when North Power Plant (P1) fails."""
        net = self.network.clone()
        bfs_res = run_bfs_disruption(net, "P1")

        self.assertIn("bfs_nodes_traversed", bfs_res)
        self.assertGreater(bfs_res["bfs_nodes_traversed"], 0)
        self.assertIn("P1", bfs_res["traversal_order"])
        
        # S1 and S4 are direct outgoing neighbors of P1
        self.assertIn("S1", bfs_res["downstream_nodes"])
        self.assertIn("S4", bfs_res["downstream_nodes"])
        
        # Check affected destinations
        self.assertIn("C1", bfs_res["affected_destinations"])

    def test_04_dijkstra_shortest_path(self):
        """Verify Dijkstra finds lowest cost path and computes bottleneck capacity."""
        net = self.network.clone()
        # Find path from P2 to C1 (Metro City)
        route = find_shortest_path(net, "P2", "C1")
        
        self.assertIsNotNone(route)
        self.assertEqual(route["source"], "P2")
        self.assertEqual(route["destination"], "C1")
        self.assertTrue(route["total_cost"] > 0)
        self.assertTrue(route["bottleneck_capacity"] > 0)
        self.assertGreaterEqual(len(route["path"]), 3)
        self.assertEqual(route["path"][0], "P2")
        self.assertEqual(route["path"][-1], "C1")

    def test_05_dijkstra_avoids_disabled_nodes(self):
        """Verify Dijkstra does not route through disabled nodes."""
        net = self.network.clone()
        net.disable_node("S1")
        
        route = find_shortest_path(net, "P1", "C1")
        if route:
            self.assertNotIn("S1", route["path"])

    def test_06_shortage_and_health_calculations(self):
        """Verify shortage engine formulas and 0-100 clamping."""
        dest_data = [
            {"id": "C1", "name": "Metro City", "demand": 80, "original_supply": 80, "recovered_supply": 80},
            {"id": "C2", "name": "Industrial Zone", "demand": 70, "original_supply": 70, "recovered_supply": 35}
        ]
        
        res = calculate_shortages(self.network, dest_data)
        self.assertEqual(res["total_demand"], 150.0)
        self.assertEqual(res["total_recovered_supply"], 115.0)
        self.assertEqual(res["total_shortage"], 35.0)
        # Health = 115 / 150 * 100 = 76.66% -> 77%
        self.assertEqual(res["network_health"], 77)

    def test_07_route_ranking(self):
        """Verify alternative routes are ranked by multi-criteria penalty score."""
        candidates = [
            {"path": ["P2", "S2", "D1", "C1"], "path_str": "P2 → S2 → D1 → C1", "total_cost": 20, "total_delay": 4, "bottleneck_capacity": 65},
            {"path": ["P3", "S5", "D2", "C1"], "path_str": "P3 → S5 → D2 → C1", "total_cost": 30, "total_delay": 6, "bottleneck_capacity": 45}
        ]
        ranked = rank_alternative_routes(candidates, destination_demand=80, original_cost=15, original_delay=2)
        
        self.assertEqual(len(ranked), 2)
        self.assertTrue(ranked[0]["is_best"])
        self.assertEqual(ranked[0]["rank"], 1)
        self.assertEqual(ranked[1]["rank"], 2)
        self.assertLessEqual(ranked[0]["score"], ranked[1]["score"])

    def test_08_full_simulation_pipeline_supplier_failure(self):
        """Run complete disruption simulation on P1 (North Thermal Plant)."""
        sim = run_disruption_simulation(self.network, "P1")
        
        self.assertNotIn("error", sim)
        self.assertEqual(sim["disabled_node"]["id"], "P1")
        self.assertGreater(sim["total_demand"], 0)
        self.assertIn("alternatives_by_destination", sim)
        self.assertIn("algorithm_summary", sim)
        self.assertGreater(sim["algorithm_summary"]["bfs_nodes_traversed"], 0)
        self.assertGreater(sim["algorithm_summary"]["dijkstra_runs"], 0)

    def test_09_full_simulation_pipeline_substation_failure(self):
        """Run complete disruption simulation on S2 (Central Switching Station)."""
        sim = run_disruption_simulation(self.network, "S2")
        
        self.assertNotIn("error", sim)
        self.assertEqual(sim["disabled_node"]["id"], "S2")
        self.assertIn("destination_impacts", sim)

    def test_10_api_get_network(self):
        """Test GET /api/network endpoint."""
        res = self.client.get("/api/network")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(len(data["data"]["nodes"]), 16)

    def test_11_api_simulate_endpoint(self):
        """Test POST /api/simulate endpoint."""
        res = self.client.post(
            "/api/simulate",
            data=json.dumps({"disabled_node": "P1"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertEqual(data["simulation"]["disabled_node"]["id"], "P1")

    def test_12_api_reset_endpoint(self):
        """Test POST /api/reset endpoint."""
        res = self.client.post("/api/reset")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])

    def test_13_api_scenarios_endpoint(self):
        """Test GET /api/scenarios endpoint."""
        res = self.client.get("/api/scenarios")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["scenarios"]), 2)


if __name__ == "__main__":
    unittest.main()
