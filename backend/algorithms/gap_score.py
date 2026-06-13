"""
Gap Score Algorithm
Calculates humanitarian gaps in disaster zones
(Identifies where medicine is NEEDED but NOT AVAILABLE)
"""

def calculate_gap_score(
    disaster_severity: float,
    population_affected: float,
    aid_received: float,
    ngo_presence: float,
    media_coverage: float
) -> float:
    """
    Calculate the humanitarian gap score for a disaster zone
    
    Formula:
    NEED = Disaster_Severity × Population / 100
    COVERAGE = (Aid_Received + NGO_Presence + Media_Coverage) / 3
    GAP = NEED - COVERAGE
    
    Returns: Gap score (0-100+)
    - > 75: CRITICAL (zone is abandoned)
    - 50-75: HIGH (severely underserved)
    - 30-50: MEDIUM (partially underserved)
    - < 30: LOW (adequately covered)
    """
    
    # Normalize inputs to 0-100 scale
    disaster_severity = max(0, min(100, disaster_severity))  # Clamp to 0-100
    media_coverage = max(0, min(100, media_coverage))
    
    # Calculate NEED (severity × population impact)
    # Using log scale to prevent extreme values
    import math
    
    # Normalize population affected (scale it to 0-100)
    # Assuming max disaster population is 10 million
    population_normalized = min(100, (population_affected / 100000))  # Every 100K = 1 point
    
    # NEED combines disaster severity and population impact
    need = (disaster_severity * population_normalized) / 100 * 100
    
    # Calculate COVERAGE (how much aid is already there)
    # Normalize each component
    aid_score = min(100, (aid_received / 10000))  # Every 10K aid = 1 point
    ngo_score = min(100, (ngo_presence * 25))    # Each NGO = 25 points max
    media_score = media_coverage  # Already 0-100
    
    coverage = (aid_score + ngo_score + media_score) / 3
    
    # GAP = NEED - COVERAGE
    gap = max(0, need - coverage)
    
    return gap


def batch_gap_analysis(zones: list) -> dict:
    """
    Analyze multiple zones at once
    Returns zones ranked by gap score (highest = most underserved)
    
    Input format:
    [
        {
            "zone_name": "Bihar",
            "disaster_severity": 85,
            "population_affected": 500000,
            "aid_received": 30000,
            "ngo_presence": 2,
            "media_coverage": 10
        },
        ...
    ]
    """
    results = []
    
    for zone in zones:
        gap = calculate_gap_score(
            disaster_severity=zone.get("disaster_severity", 0),
            population_affected=zone.get("population_affected", 0),
            aid_received=zone.get("aid_received", 0),
            ngo_presence=zone.get("ngo_presence", 0),
            media_coverage=zone.get("media_coverage", 0)
        )
        
        results.append({
            "zone_name": zone.get("zone_name"),
            "gap_score": round(gap, 2),
            "population": zone.get("population_affected"),
            "severity": classify_severity(gap)
        })
    
    # Sort by gap score (highest first = most critical)
    results.sort(key=lambda x: x["gap_score"], reverse=True)
    
    return {
        "total_zones": len(results),
        "zones_ranked": results,
        "most_critical": results[0] if results else None,
        "critical_count": len([z for z in results if z["gap_score"] >= 50])
    }


def classify_severity(gap_score: float) -> str:
    """Classify gap severity level"""
    if gap_score >= 75:
        return "🔴 CRITICAL"
    elif gap_score >= 50:
        return "🟠 HIGH"
    elif gap_score >= 30:
        return "🟡 MEDIUM"
    else:
        return "🟢 LOW"