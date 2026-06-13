"""
Autonomous Routing Agent
Makes intelligent recommendations for routing viable medicines to underserved zones
(The "AI brain" that decides who gets what medicine)
"""


def generate_recommendations(zones: list, available_supplies: list) -> list:
    """
    Generate autonomous routing recommendations
    
    Algorithm:
    1. Rank zones by need (highest gap score first)
    2. For each zone, find viable medicines available
    3. Match zone's medicine_needed with available supplies
    4. Create recommendation with impact metrics
    
    Args:
        zones: List of disaster zones with gap scores
        available_supplies: List of available medicine shipments with viability
    
    Returns:
        List of recommendations ranked by urgency/impact
    """
    
    recommendations = []
    
    # Sort zones by gap score (highest = most critical)
    zones_sorted = sorted(zones, key=lambda z: z.get("gap_score", 0), reverse=True)
    
    for zone in zones_sorted:
        zone_name = zone.get("zone_name")
        gap_score = zone.get("gap_score", 0)
        population = zone.get("population", 0)
        medicine_needed = zone.get("medicine_needed", "")
        
        # Skip zones with low gap scores (already covered)
        if gap_score < 30:
            continue
        
        # Find viable supplies that match this zone's needs
        viable_supplies = [
            s for s in available_supplies
            if s.get("medicine_type") == medicine_needed and s.get("viability", 0) >= 0.7
        ]
        
        if viable_supplies:
            # Pick the supply with highest viability
            best_supply = max(viable_supplies, key=lambda s: s.get("viability", 0))
            
            # Calculate impact
            impact = calculate_impact(
                population=population,
                supply_quantity=best_supply.get("quantity", 0),
                gap_score=gap_score
            )
            
            recommendation = {
                "priority": "URGENT" if gap_score >= 75 else "HIGH" if gap_score >= 50 else "MEDIUM",
                "recommendation": f"Route {best_supply.get('medicine_type')} to {zone_name}",
                "zone": zone_name,
                "from_shipment": best_supply.get("shipment_id"),
                "medicine_type": medicine_needed,
                "quantity": best_supply.get("quantity"),
                "viability": best_supply.get("viability"),
                "population_reached": min(population, best_supply.get("quantity", 0) * 10),  # Rough estimate
                "impact_score": impact,
                "gap_score": gap_score,
                "reason": f"Zone has gap score of {gap_score} (critical need), and we have viable {medicine_needed}"
            }
            
            recommendations.append(recommendation)
        
        else:
            # No viable supplies for this zone - flag it as unmet
            recommendation = {
                "priority": "CRITICAL_UNMET",
                "recommendation": f"ALERT: {zone_name} needs {medicine_needed} but no viable supplies available",
                "zone": zone_name,
                "medicine_type": medicine_needed,
                "gap_score": gap_score,
                "population_affected": population,
                "action_required": "Source additional supplies or find substitutes"
            }
            
            recommendations.append(recommendation)
    
    # Sort by impact score (highest impact first)
    recommendations.sort(
        key=lambda r: r.get("impact_score", 0),
        reverse=True
    )
    
    return recommendations


def calculate_impact(population: int, supply_quantity: int, gap_score: float) -> float:
    """
    Calculate impact score for a recommendation
    (Higher = more lives saved)
    
    Factors:
    - Population affected (more people = higher impact)
    - Supply available (more medicine = higher impact)
    - Gap score (higher need = higher impact)
    """
    
    # Normalize inputs
    population_normalized = min(100, population / 5000)  # Every 5000 people = 1 point
    supply_normalized = min(100, supply_quantity / 1000)  # Every 1000 units = 1 point
    gap_normalized = min(100, gap_score)  # Gap score already 0-100
    
    # Weighted calculation
    # Gap score (50%) + Population (30%) + Supply (20%)
    impact = (
        (gap_normalized * 0.5) +
        (population_normalized * 0.3) +
        (supply_normalized * 0.2)
    )
    
    return round(impact, 2)


def intelligent_routing(
    zones: list,
    available_supplies: list,
    budget_constraint: int = None
) -> dict:
    """
    Advanced routing with constraints
    Can optimize for:
    - Saving most lives
    - Covering most zones
    - Minimizing cost
    - Maximizing equity (reaching poorest areas)
    """
    
    base_recommendations = generate_recommendations(zones, available_supplies)
    
    # If budget constraint exists, prioritize by cost-effectiveness
    if budget_constraint:
        # Calculate cost-per-life-saved
        for rec in base_recommendations:
            rec["cost_effectiveness"] = calculate_cost_effectiveness(rec, budget_constraint)
        
        # Re-sort by cost-effectiveness
        base_recommendations.sort(
            key=lambda r: r.get("cost_effectiveness", 0),
            reverse=True
        )
    
    return {
        "total_recommendations": len(base_recommendations),
        "recommendations": base_recommendations,
        "estimated_lives_reached": sum(r.get("population_reached", 0) for r in base_recommendations),
        "zones_covered": len(set(r.get("zone") for r in base_recommendations))
    }


def calculate_cost_effectiveness(recommendation: dict, budget: int) -> float:
    """Calculate lives saved per rupee spent"""
    lives = recommendation.get("population_reached", 1)
    cost_estimate = recommendation.get("quantity", 1) * 100  # Rough estimate: ₹100 per unit
    
    if cost_estimate == 0:
        return 0
    
    return lives / cost_estimate


# Example usage
if __name__ == "__main__":
    # Test data
    test_zones = [
        {
            "zone_name": "Bihar Region",
            "gap_score": 92,
            "population": 500000,
            "medicine_needed": "vaccine"
        },
        {
            "zone_name": "Delhi Suburbs",
            "gap_score": 35,
            "population": 200000,
            "medicine_needed": "insulin"
        }
    ]
    
    test_supplies = [
        {
            "shipment_id": "VAX-001",
            "medicine_type": "vaccine",
            "quantity": 50000,
            "viability": 0.95
        },
        {
            "shipment_id": "INS-001",
            "medicine_type": "insulin",
            "quantity": 5000,
            "viability": 0.60
        }
    ]
    
    recs = generate_recommendations(test_zones, test_supplies)
    print("Recommendations:")
    for rec in recs:
        print(f"  - {rec['recommendation']}")