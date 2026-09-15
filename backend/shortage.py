"""
GridGuard Shortage Engine & Grid Health Calculation
Calculates capacity constraints, remaining shortages, and global health metrics.
"""

from typing import Dict, List, Any
from .network import EnergyNetwork


def calculate_shortages(
    network: EnergyNetwork,
    destinations_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calculates supply vs demand breakdown for each destination and aggregate totals.
    """
    total_demand = 0.0
    total_recovered = 0.0
    total_shortage = 0.0
    destination_breakdown = []

    for d_info in destinations_data:
        dest_id = d_info["id"]
        demand = float(d_info.get("demand", 0.0))
        original_supply = float(d_info.get("original_supply", demand))
        recovered_supply = float(d_info.get("recovered_supply", 0.0))
        
        # Recovered supply cannot exceed demand for coverage calculations
        effective_supply = min(demand, recovered_supply)
        remaining_shortage = max(0.0, demand - effective_supply)
        
        coverage = (effective_supply / demand * 100.0) if demand > 0 else 100.0
        coverage = round(min(100.0, max(0.0, coverage)), 1)

        total_demand += demand
        total_recovered += effective_supply
        total_shortage += remaining_shortage

        destination_breakdown.append({
            "destination": dest_id,
            "name": d_info.get("name", dest_id),
            "demand": demand,
            "original_supply": original_supply,
            "recovered_supply": round(effective_supply, 1),
            "remaining_shortage": round(remaining_shortage, 1),
            "coverage": coverage
        })

    health_score = calculate_network_health(total_demand, total_recovered)

    return {
        "total_demand": round(total_demand, 1),
        "total_recovered_supply": round(total_recovered, 1),
        "total_shortage": round(total_shortage, 1),
        "network_health": health_score,
        "destinations": destination_breakdown
    }


def calculate_network_health(total_demand: float, total_satisfied: float) -> int:
    """
    Computes a network health score from 0 to 100 based on satisfied grid demand.
    """
    if total_demand <= 0:
        return 100
    ratio = total_satisfied / total_demand
    clamped_score = max(0.0, min(1.0, ratio)) * 100.0
    return int(round(clamped_score))
