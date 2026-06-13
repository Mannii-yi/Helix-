"""
helix - Real-time medical disaster response
FastAPI Backend Server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import json

# Import our custom algorithms
from algorithms.gap_score import calculate_gap_score
from algorithms.viability_predictor import predict_medicine_viability
from algorithms.routing_agent import generate_recommendations
from data_sources.gdacs_fetcher import fetch_disasters
from data_sources.synthetic_data import generate_synthetic_cold_chain_data

# Initialize FastAPI app
app = FastAPI(
    title="helix",
    description="Real-time medical disaster response intelligence",
    version="1.0.0"
)

# Enable CORS (so Streamlit frontend can talk to this backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (safe for hackathon)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== ROUTES ====================

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "🧬 Helix is alive",
        "message": "Real-time medical disaster response",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/disasters")
async def get_disasters():
    """
    Fetch real disaster data from GDACS
    Returns: List of active disasters worldwide
    """
    try:
        disasters = fetch_disasters()
        return {
            "status": "success",
            "count": len(disasters),
            "disasters": disasters,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze-zone")
def analyze_zone(data: dict):
    """
    Analyze a disaster zone for humanitarian gaps
    
    Expected input:
    {
        "zone_name": "Bihar Region",
        "disaster_severity": 85,
        "population_affected": 500000,
        "aid_received": 30000,
        "ngo_presence": 2,
        "media_coverage": 10
    }
    """
    try:
        gap_score = calculate_gap_score(
            disaster_severity=data.get("disaster_severity", 0),
            population_affected=data.get("population_affected", 0),
            aid_received=data.get("aid_received", 0),
            ngo_presence=data.get("ngo_presence", 0),
            media_coverage=data.get("media_coverage", 0)
        )
        
        return {
            "status": "success",
            "zone": data.get("zone_name"),
            "gap_score": round(gap_score, 2),
            "severity": classify_gap(gap_score),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/check-medicine-viability")
def check_medicine_viability(data: dict):
    """
    Check if a medicine shipment is still viable
    
    Expected input:
    {
        "medicine_type": "vaccine",
        "temperature_logs": [2, 2, 2, 15, 20, 25, 2, 2],
        "duration_minutes": 480
    }
    """
    try:
        viability_score = predict_medicine_viability(
            medicine_type=data.get("medicine_type", "vaccine"),
            temperature_logs=data.get("temperature_logs", []),
            duration_minutes=data.get("duration_minutes", 0)
        )
        
        status = "VIABLE" if viability_score >= 0.7 else "COMPROMISED" if viability_score >= 0.3 else "DESTROYED"
        
        return {
            "status": "success",
            "medicine_type": data.get("medicine_type"),
            "viability_score": round(viability_score, 3),
            "status_flag": status,
            "safe_to_use": viability_score >= 0.7,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/generate-recommendations")
def generate_recs(data: dict):
    """
    Generate autonomous routing recommendations
    
    Expected input:
    {
        "zones": [
            {"name": "Zone A", "gap_score": 92, "medicine_needed": "insulin"},
            {"name": "Zone B", "gap_score": 15, "medicine_needed": "vaccine"}
        ],
        "available_supplies": [
            {"medicine_type": "insulin", "quantity": 5000, "viability": 0.95},
            {"medicine_type": "vaccine", "quantity": 10000, "viability": 0.4}
        ]
    }
    """
    try:
        recommendations = generate_recommendations(
            zones=data.get("zones", []),
            available_supplies=data.get("available_supplies", [])
        )
        
        return {
            "status": "success",
            "recommendations": recommendations,
            "count": len(recommendations),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/mock-scenario/{scenario_type}")
def get_mock_scenario(scenario_type: str):
    """
    Get a mock disaster scenario for testing
    
    Scenarios: 
    - "earthquake" 
    - "flood"
    - "storm"
    - "combined"
    """
    try:
        cold_chain_data = generate_synthetic_cold_chain_data(scenario_type)
        return {
            "status": "success",
            "scenario": scenario_type,
            "data": cold_chain_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "api": "helix-backend",
        "version": "1.0.0",
        "endpoints_available": 6,
        "timestamp": datetime.now().isoformat()
    }

# ==================== HELPER FUNCTIONS ====================

def classify_gap(gap_score: float) -> str:
    """Classify the severity level based on gap score"""
    if gap_score >= 75:
        return "CRITICAL - ZONE ABANDONED"
    elif gap_score >= 50:
        return "HIGH - SEVERELY UNDERSERVED"
    elif gap_score >= 30:
        return "MEDIUM - PARTIALLY UNDERSERVED"
    else:
        return "LOW - ADEQUATELY COVERED"

# ==================== STARTUP ====================

if __name__ == "__main__":
    print("""
    
    ╔═══════════════════════════════════════╗
    ║         🧬 helix Backend              ║
    ║  Medical Disaster Response Intelligence║
    ╚═══════════════════════════════════════╝
    
    Starting FastAPI server...
    📍 API will be available at: http://localhost:8000
    📚 Documentation at: http://localhost:8000/docs
    
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )