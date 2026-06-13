"""
GDACS Fetcher
Fetches real-time disaster data from GDACS (Global Disaster Alert and Coordination System)
This is a FREE public API maintained by the UN
"""

import requests
import json
from datetime import datetime
from typing import List, Dict


def fetch_disasters() -> List[Dict]:
    """
    Fetch active disasters from GDACS API
    
    Returns:
        List of active disasters with details
    """
    
    try:
        # GDACS public API (completely free, no auth needed)
        url = "https://www.gdacs.org/api/v1/events"
        
        # Fetch with timeout
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Parse and format disasters
        disasters = []
        
        if "events" in data:
            for event in data["events"][:20]:  # Limit to recent 20 events
                disaster = {
                    "id": event.get("eventid"),
                    "name": event.get("name"),
                    "type": event.get("eventtype"),
                    "country": event.get("country"),
                    "latitude": float(event.get("lat", 0)),
                    "longitude": float(event.get("lon", 0)),
                    "severity": event.get("severity"),
                    "deaths": event.get("deaths", 0),
                    "affected": event.get("affected", 0),
                    "date": event.get("date"),
                    "description": event.get("description")
                }
                
                disasters.append(disaster)
        
        return disasters
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching GDACS data: {e}")
        # Return mock data if API fails
        return get_mock_disasters()


def get_mock_disasters() -> List[Dict]:
    """
    Returns mock disaster data for testing
    (Use when GDACS API is unreachable)
    """
    
    return [
        {
            "id": "MOCK-001",
            "name": "Monsoon Floods - Bihar Region",
            "type": "flood",
            "country": "India",
            "latitude": 25.5941,
            "longitude": 85.1376,
            "severity": "high",
            "deaths": 145,
            "affected": 500000,
            "date": datetime.now().isoformat(),
            "description": "Severe monsoon flooding in Bihar region affecting multiple districts"
        },
        {
            "id": "MOCK-002",
            "name": "Earthquake - Turkey",
            "type": "earthquake",
            "country": "Turkey",
            "latitude": 38.0,
            "longitude": 35.0,
            "severity": "extreme",
            "deaths": 5000,
            "affected": 2000000,
            "date": "2024-01-15",
            "description": "Major earthquake affecting central Turkey"
        },
        {
            "id": "MOCK-003",
            "name": "Cyclone - Bangladesh",
            "type": "storm",
            "country": "Bangladesh",
            "latitude": 22.3456,
            "longitude": 91.7654,
            "severity": "high",
            "deaths": 234,
            "affected": 300000,
            "date": datetime.now().isoformat(),
            "description": "Strong tropical cyclone affecting coastal regions"
        }
    ]


def enrich_disaster_with_gap_analysis(disaster: Dict) -> Dict:
    """
    Add humanitarian gap analysis to a disaster
    Simulates real gap data (would come from NGO databases)
    """
    
    from algorithms.gap_score import calculate_gap_score
    
    # Simulate aid presence data (in real deployment, query NGO databases)
    aid_received = max(0, disaster.get("affected", 0) * 0.1)  # Assume 10% have received aid
    ngo_presence = max(1, disaster.get("affected", 0) // 200000)  # 1 NGO per 200k people
    media_coverage = 50 if "Turkey" in disaster.get("name", "") or "earthquake" in disaster.get("type", "").lower() else 10
    
    gap_score = calculate_gap_score(
        disaster_severity=100 if disaster.get("severity") == "extreme" else 80 if disaster.get("severity") == "high" else 50,
        population_affected=disaster.get("affected", 0),
        aid_received=aid_received,
        ngo_presence=ngo_presence,
        media_coverage=media_coverage
    )
    
    disaster["gap_score"] = round(gap_score, 2)
    disaster["aid_received"] = int(aid_received)
    disaster["ngo_presence"] = int(ngo_presence)
    disaster["media_coverage"] = media_coverage
    
    return disaster


def fetch_disasters_with_analysis() -> List[Dict]:
    """
    Fetch disasters and enrich with gap analysis
    """
    disasters = fetch_disasters()
    
    enriched = []
    for disaster in disasters:
        enriched.append(enrich_disaster_with_gap_analysis(disaster))
    
    return enriched


if __name__ == "__main__":
    # Test the fetcher
    print("Fetching disasters from GDACS...")
    disasters = fetch_disasters_with_analysis()
    
    print(f"\nFound {len(disasters)} active disasters:\n")
    for d in disasters[:5]:
        print(f"📍 {d.get('name')}")
        print(f"   Type: {d.get('type')} | Severity: {d.get('severity')}")
        print(f"   Affected: {d.get('affected'):,} people")
        print(f"   Gap Score: {d.get('gap_score', 'N/A')}")
        print()