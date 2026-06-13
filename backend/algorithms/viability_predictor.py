"""
Medicine Viability Predictor
Determines if medicine shipments are still safe to use based on temperature exposure
Uses WHO standards for safe temperature ranges
"""

# WHO Safe Temperature Ranges (in Celsius)
MEDICINE_THRESHOLDS = {
    "vaccine": {
        "safe_range": (2, 8),
        "critical_temp": 10,
        "critical_duration": 30,  # minutes
        "description": "COVID, Polio, MMR vaccines"
    },
    "insulin": {
        "safe_range": (2, 8),
        "critical_temp": 25,
        "critical_duration": 60,
        "description": "Diabetes medication"
    },
    "blood": {
        "safe_range": (1, 6),
        "critical_temp": 10,
        "critical_duration": 15,
        "description": "Blood units for transfusion"
    },
    "mrna": {
        "safe_range": (-80, -60),  # Ultra-cold storage
        "critical_temp": -20,
        "critical_duration": 720,  # 12 hours
        "description": "mRNA vaccines (Pfizer, Moderna)"
    },
    "antibiotic": {
        "safe_range": (15, 25),
        "critical_temp": 35,
        "critical_duration": 120,
        "description": "Antibiotics, general medicines"
    }
}


def predict_medicine_viability(
    medicine_type: str,
    temperature_logs: list,
    duration_minutes: int
) -> float:
    """
    Predict viability of medicine based on temperature exposure
    
    Args:
        medicine_type: Type of medicine (vaccine, insulin, blood, mrna, antibiotic)
        temperature_logs: List of temperature readings (°C)
        duration_minutes: Total duration of exposure
    
    Returns:
        viability_score: 0.0 = destroyed, 1.0 = perfect condition
    
    Example:
        >>> temps = [2, 2, 2, 15, 20, 25, 2, 2]  # Temp spike in middle
        >>> predict_medicine_viability("vaccine", temps, 480)
        0.35  # Compromised (damaged by heat)
    """
    
    if medicine_type not in MEDICINE_THRESHOLDS:
        raise ValueError(f"Unknown medicine type: {medicine_type}")
    
    if not temperature_logs or len(temperature_logs) == 0:
        return 1.0  # No data = assume perfect
    
    threshold = MEDICINE_THRESHOLDS[medicine_type]
    safe_min, safe_max = threshold["safe_range"]
    critical_temp = threshold["critical_temp"]
    critical_duration = threshold["critical_duration"]
    
    # Calculate damage based on temperature exposure
    max_temp = max(temperature_logs)
    min_temp = min(temperature_logs)
    
    # Check if temperature went outside safe range
    damage_score = 0.0
    
    # Count how many readings exceeded safe range
    unsafe_readings = sum(1 for t in temperature_logs if t < safe_min or t > safe_max)
    unsafe_percentage = (unsafe_readings / len(temperature_logs)) * 100
    
    # If completely within safe range, no damage
    if max_temp <= safe_max and min_temp >= safe_min:
        return 1.0
    
    # Calculate damage severity
    # Factor 1: How far outside range? (temperature deviation)
    if max_temp > safe_max:
        temp_overage = max_temp - safe_max
        overage_severity = min(1.0, temp_overage / (critical_temp - safe_max))
    else:
        temp_overage = safe_min - min_temp
        overage_severity = min(1.0, temp_overage / (safe_min - critical_temp)) if (safe_min - critical_temp) > 0 else 0
    
    # Factor 2: Duration of exposure (what % of time was it bad?)
    duration_severity = unsafe_percentage / 100
    
    # Factor 3: How critical was the temperature spike?
    if max_temp > critical_temp:
        duration_over_critical = sum(1 for t in temperature_logs if t > critical_temp)
        duration_over_critical_minutes = (duration_over_critical / len(temperature_logs)) * duration_minutes
        duration_over_severity = min(1.0, duration_over_critical_minutes / critical_duration)
    else:
        duration_over_severity = 0
    
    # Combine factors (weighted average)
    # Temperature severity (40%) + Duration at unsafe (30%) + Duration at critical (30%)
    damage_score = (
        (overage_severity * 0.4) +
        (duration_severity * 0.3) +
        (duration_over_severity * 0.3)
    )
    
    # Viability = 1 - damage (clamped between 0 and 1)
    viability = max(0.0, 1.0 - damage_score)
    
    return round(viability, 3)


def batch_viability_check(shipments: list) -> dict:
    """
    Check viability of multiple medicine shipments
    
    Input format:
    [
        {
            "shipment_id": "VAX-001",
            "medicine_type": "vaccine",
            "temperature_logs": [2, 2, 2, 15, 20, 25, 2, 2],
            "duration_minutes": 480
        },
        ...
    ]
    """
    results = []
    
    for shipment in shipments:
        viability = predict_medicine_viability(
            medicine_type=shipment.get("medicine_type"),
            temperature_logs=shipment.get("temperature_logs", []),
            duration_minutes=shipment.get("duration_minutes", 0)
        )
        
        results.append({
            "shipment_id": shipment.get("shipment_id"),
            "medicine_type": shipment.get("medicine_type"),
            "viability_score": viability,
            "status": get_viability_status(viability),
            "safe_to_use": viability >= 0.7,
            "quantity": shipment.get("quantity")
        })
    
    return {
        "total_shipments": len(results),
        "viable_count": len([s for s in results if s["safe_to_use"]]),
        "compromised_count": len([s for s in results if 0.3 <= s["viability_score"] < 0.7]),
        "destroyed_count": len([s for s in results if s["viability_score"] < 0.3]),
        "shipments": results
    }


def get_viability_status(score: float) -> str:
    """Get human-readable viability status"""
    if score >= 0.9:
        return "✅ PERFECT - Use immediately"
    elif score >= 0.7:
        return "✅ VIABLE - Safe to use"
    elif score >= 0.5:
        return "⚠️ COMPROMISED - Use with caution"
    elif score >= 0.3:
        return "⚠️ DAMAGED - Consider discarding"
    else:
        return "❌ DESTROYED - Do not use"


# Test function
if __name__ == "__main__":
    # Test scenario: vaccine exposed to heat spike
    test_temps = [2, 2, 2, 15, 20, 25, 2, 2]
    viability = predict_medicine_viability("vaccine", test_temps, 480)
    print(f"Vaccine viability: {viability}")
    print(f"Status: {get_viability_status(viability)}")