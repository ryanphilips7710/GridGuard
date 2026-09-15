"""
GridGuard Route Ranking & Scoring Engine
Ranks alternative supply routes based on cost delta, latency delta, and capacity feasibility.
"""

from typing import Dict, List, Any


def rank_alternative_routes(
    candidate_routes: List[Dict[str, Any]],
    destination_demand: float,
    original_cost: float,
    original_delay: float
) -> List[Dict[str, Any]]:
    """
    Ranks candidate alternative supply routes using a transparent multi-criteria formula.
    
    Formula:
      Cost Delta (d_cost) = max(0, route.total_cost - original_cost)
      Delay Delta (d_delay) = max(0, route.total_delay - original_delay)
      Shortage = max(0, destination_demand - route.bottleneck_capacity)
      
      Score = (d_cost * 0.4) + (d_delay * 15 * 0.3) + (Shortage * 1.5 * 0.3)
      (Lower score is better)
    """
    if not candidate_routes:
        return []

    scored_routes = []

    for route in candidate_routes:
        route_cost = float(route.get("total_cost", 0.0))
        route_delay = float(route.get("total_delay", 0.0))
        bottleneck_cap = float(route.get("bottleneck_capacity", 0.0))

        # Additional cost and delay compared to nominal baseline
        delta_cost = round(max(0.0, route_cost - original_cost), 1)
        delta_delay = round(max(0.0, route_delay - original_delay), 1)

        # How much supply this route can deliver
        delivered_supply = min(destination_demand, bottleneck_cap)
        route_shortage = round(max(0.0, destination_demand - delivered_supply), 1)
        coverage_pct = round((delivered_supply / destination_demand * 100.0) if destination_demand > 0 else 100.0, 1)

        # Transparent linear composite penalty score
        # 40% cost weight, 30% latency weight, 30% shortage penalty
        score = (delta_cost * 0.4) + (delta_delay * 15.0 * 0.3) + (route_shortage * 2.0 * 0.3)

        # Build human-readable explanation
        reasons = []
        if route_shortage == 0:
            reasons.append("100% capacity coverage")
        else:
            reasons.append(f"{route_shortage} MW deficit due to {bottleneck_cap} MW bottleneck")

        if delta_cost == 0:
            reasons.append("Nominal transmission cost")
        else:
            reasons.append(f"+₹{delta_cost} cost delta")

        if delta_delay == 0:
            reasons.append("Zero added latency")
        else:
            reasons.append(f"+{delta_delay}h delay")

        explanation = "; ".join(reasons)

        scored_route = {
            **route,
            "original_cost": round(original_cost, 1),
            "original_delay": round(original_delay, 1),
            "additional_cost": delta_cost,
            "additional_delay": delta_delay,
            "recovered_supply": round(delivered_supply, 1),
            "remaining_shortage": route_shortage,
            "coverage": coverage_pct,
            "score": round(score, 2),
            "rank_explanation": explanation
        }
        scored_routes.append(scored_route)

    # Sort ascending by composite penalty score (best first)
    scored_routes.sort(key=lambda r: (r["score"], -r["recovered_supply"], r["total_cost"]))

    # Assign rank numbers
    for idx, r in enumerate(scored_routes, start=1):
        r["rank"] = idx
        r["is_best"] = (idx == 1)

    return scored_routes
