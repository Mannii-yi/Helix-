"""
Synthetic Data Generator
Creates realistic cold chain failure scenarios for testing
(Used when real IoT data isn't available - perfect for hackathons!)
"""

import random
from datetime import datetime, timedelta


def generate_synthetic_cold_chain_data(scenario_type: str = "combined") -> dict:
    """
    Generate realistic synthetic temperature logs for different disaster scenarios
    
    Scenarios:
    - "earthquake": Power outage, gradual warming
    - "flood": Complete cold chain failure, rapid temperature spike
    - "storm": Intermittent power loss, fluctuating temperatures
    - "transport": Temperature spike during transport
    - "combined": Mixed failures
    """
    
    if scenario_type == "earthquake":
        return scenario_earthquake()
    elif scenario_type == "flood":
        return scenario_flood()
    elif scenario_type == "storm":
        return scenario_storm()
    elif scenario_type == "transport":
        return scenario_transport()
    else:  # "combined"
        return scenario_combined()


def scenario_earthquake() -> dict:
    """
    Earthquake scenario:
    - Initial stable temperature (power working)
    - Gradual temperature rise (power loss, backup fails)
    - Extended high temperature period
    """
    
    temps = []
    # First 2 hours: Normal
    temps.extend([2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
    
    # Next 4 hours: Gradual warmup (generator failing)
    temps.extend([5, 8, 12, 15, 18, 20, 22, 23, 24, 25, 25, 25])
    
    # Next 6 hours: Stuck at high temp (cold chain dead)
    temps.extend([25] * 18)
    
    # Last 2 hours: Cooling kicks in
    temps.extend([20, 15, 10, 8, 5, 2, 2, 2])
    
    return {
        "scenario": "Earthquake - Power Loss",
        "description": "Major earthquake causes power outage, backup system fails, 12-hour temperature exposure",
        "zone": "Delhi Region",
        "timestamp": datetime.now().isoformat(),
        "duration_hours": 14,
        "duration_minutes": 14 * 60,
        "temperature_logs": temps,
        "medicines": [
            {
                "shipment_id": "VAX-EARTH-001",
                "type": "vaccine",
                "quantity": 10000,
                "expected_damage": "high"
            },
            {
                "shipment_id": "INS-EARTH-001",
                "type": "insulin",
                "quantity": 5000,
                "expected_damage": "high"
            }
        ]
    }


def scenario_flood() -> dict:
    """
    Flood scenario:
    - Rapid rise in temperature (water damage, cooling loss)
    - Temperature spikes above safe range quickly
    - Extended high temperature exposure
    """
    
    temps = []
    # First hour: Normal
    temps.extend([2, 2, 2, 2, 2])
    
    # Rapid spike (flooding occurs)
    temps.extend([10, 20, 30, 35, 35])
    
    # Extended high temperature (6 hours)
    temps.extend([35] * 18)
    
    # Recovery (reaching safe zone)
    temps.extend([30, 25, 20, 15, 10, 5, 2])
    
    return {
        "scenario": "Monsoon Flooding - Cold Chain Destroyed",
        "description": "Flash flooding destroys refrigeration, medicines exposed to high heat for 8+ hours",
        "zone": "Bihar Region",
        "timestamp": datetime.now().isoformat(),
        "duration_hours": 8,
        "duration_minutes": 8 * 60,
        "temperature_logs": temps,
        "medicines": [
            {
                "shipment_id": "VAX-FLOOD-001",
                "type": "vaccine",
                "quantity": 50000,
                "expected_damage": "critical"
            },
            {
                "shipment_id": "BLOOD-FLOOD-001",
                "type": "blood",
                "quantity": 1000,
                "expected_damage": "critical"
            }
        ]
    }


def scenario_storm() -> dict:
    """
    Storm scenario:
    - Intermittent power loss
    - Fluctuating temperatures
    - Multiple periods of cooling loss
    """
    
    temps = []
    
    # Cycle 1: Normal -> Power loss -> Recovery
    temps.extend([2, 2, 2, 2, 2])
    temps.extend([8, 15, 18, 15, 10, 5, 2, 2])
    
    # Cycle 2: Normal -> Power loss -> Recovery
    temps.extend([2, 2, 2, 2, 2])
    temps.extend([10, 18, 20, 18, 12, 5, 2, 2])
    
    # Cycle 3: Normal -> Power loss -> Recovery
    temps.extend([2, 2, 2, 2, 2])
    temps.extend([12, 20, 22, 20, 14, 5, 2, 2])
    
    return {
        "scenario": "Cyclone - Intermittent Power Loss",
        "description": "High-speed winds cause repeated power failures, multiple temperature cycles",
        "zone": "Tamil Nadu Coast",
        "timestamp": datetime.now().isoformat(),
        "duration_hours": 16,
        "duration_minutes": 16 * 60,
        "temperature_logs": temps,
        "medicines": [
            {
                "shipment_id": "VAX-STORM-001",
                "type": "vaccine",
                "quantity": 25000,
                "expected_damage": "medium"
            }
        ]
    }


def scenario_transport() -> dict:
    """
    Transport scenario:
    - Temperature stable during storage
    - Temperature spike during transport/delivery
    - Brief but significant exposure
    """
    
    temps = []
    
    # Storage: Cold and stable
    temps.extend([2, 2, 2, 2, 2, 2, 2, 2, 2, 2])
    
    # Transport begins: Temperature rises
    temps.extend([8, 15, 20, 25, 28, 28, 28, 25, 20, 15, 10, 5])
    
    # Delivery and rest
    temps.extend([2, 2, 2, 2, 2, 2, 2])
    
    return {
        "scenario": "Transport Failure - Heat Exposure",
        "description": "Vehicle refrigeration fails during transport, medicines exposed to ambient heat for 3+ hours",
        "zone": "In Transit: Mumbai to Delhi",
        "timestamp": datetime.now().isoformat(),
        "duration_hours": 7,
        "duration_minutes": 7 * 60,
        "temperature_logs": temps,
        "medicines": [
            {
                "shipment_id": "INS-TRANS-001",
                "type": "insulin",
                "quantity": 8000,
                "expected_damage": "medium-high"
            }
        ]
    }


def scenario_combined() -> dict:
    """
    Combined scenario:
    - Mix of all previous failures
    - Realistic multi-factor disaster
    """
    
    temps = []
    
    # Pre-disaster: Normal operation
    temps.extend([2] * 10)
    
    # Earthquake hits: Power loss, gradual warmup
    temps.extend([5, 10, 15, 20, 22, 24, 25, 25, 25])
    
    # Flooding: Additional temperature spike
    temps.extend([30, 32, 35, 35, 35])
    
    # Partial recovery: Manual cooling attempts
    temps.extend([28, 25, 20, 15, 10])
    
    # Aftershock: Power loss again
    temps.extend([18, 25, 28, 28, 28])
    
    # Final recovery
    temps.extend([20, 10, 5, 2, 2])
    
    return {
        "scenario": "Major Disaster - Combined Failures",
        "description": "Earthquake + flooding + aftershocks = multiple cold chain failures, extended exposure",
        "zone": "Kathmandu Valley, Nepal",
        "timestamp": datetime.now().isoformat(),
        "duration_hours": 12,
        "duration_minutes": 12 * 60,
        "temperature_logs": temps,
        "medicines": [
            {
                "shipment_id": "VAX-COMB-001",
                "type": "vaccine",
                "quantity": 100000,
                "expected_damage": "critical"
            },
            {
                "shipment_id": "INS-COMB-001",
                "type": "insulin",
                "quantity": 15000,
                "expected_damage": "high"
            },
            {
                "shipment_id": "BLOOD-COMB-001",
                "type": "blood",
                "quantity": 5000,
                "expected_damage": "critical"
            }
        ]
    }


def generate_random_sensor_data(duration_minutes: int = 480) -> dict:
    """
    Generate random but realistic temperature data
    Good for stress-testing the system
    """
    
    temps = []
    current_temp = 2  # Start cold
    
    for _ in range(duration_minutes // 15):  # 15-min intervals
        # Random walk: temperature drifts slightly each period
        change = random.choice(
            [0, 0, 0, 0, 0] +  # Most likely no change
            [1, 2, -1, -2] +   # Occasional small changes
            [5, 10, -5] +      # Less frequent larger changes
            [20]               # Rare extreme events
        )
        
        current_temp = max(-20, min(40, current_temp + change))  # Clamp to realistic range
        temps.append(round(current_temp, 1))
    
    return {
        "scenario": "Random Sensor Data",
        "description": f"Randomly generated temperature data over {duration_minutes} minutes",
        "temperature_logs": temps,
        "duration_minutes": duration_minutes
    }


if __name__ == "__main__":
    # Test all scenarios
    scenarios = ["earthquake", "flood", "storm", "transport", "combined"]
    
    for scenario in scenarios:
        data = generate_synthetic_cold_chain_data(scenario)
        print(f"\n{data['scenario']}")
        print(f"  Duration: {data['duration_hours']} hours")
        print(f"  Temps: {data['temperature_logs']}")
        print(f"  Medicines at risk: {len(data.get('medicines', []))}")