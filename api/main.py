"""
UniPLC API - REST endpoint for protocol translation
Serves both the API and the web dashboard
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import sys
import os

# Add parent to path for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from agent.translator import ProtocolTranslator, UnifiedMetrics
from simulators.modbus_simulator import generate_modbus_dump, get_structured_data as modbus_data
from simulators.s7comm_simulator import generate_s7_raw_dump, get_structured_data as s7comm_data
from simulators.opcua_simulator import generate_opcua_dump, get_structured_data as opcua_data

app = FastAPI(
    title="UniPLC API",
    description="AI-powered industrial protocol translation",
    version="0.1.0"
)

# Initialize translator (lazy - only when API key is available)
translator = None


def get_translator():
    global translator
    if translator is None:
        try:
            translator = ProtocolTranslator()
        except Exception:
            return None
    return translator


class TranslateRequest(BaseModel):
    raw_dump: str
    machine_hint: Optional[str] = None


class TranslateResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[str] = None


class SimulatedDump(BaseModel):
    protocol: str
    raw_dump: str
    machine_id: str


# Serve the web dashboard
@app.get("/")
async def serve_dashboard():
    return FileResponse(os.path.join(BASE_DIR, "web", "index.html"))


@app.get("/health")
async def health():
    return {"status": "healthy", "api_key_configured": get_translator() is not None}


# Simulation endpoints (work without API key)
@app.get("/api/simulate/{protocol}")
async def simulate_protocol(protocol: str):
    """
    Generate simulated data for a protocol.
    Works without API key - for demo purposes.
    """
    if protocol == "modbus":
        data = modbus_data()
        return SimulatedDump(
            protocol="modbus",
            raw_dump=data["raw_dump"],
            machine_id="linea1-fresadora"
        )
    elif protocol == "s7comm":
        data = s7comm_data()
        return SimulatedDump(
            protocol="s7comm",
            raw_dump=data["raw_dump"],
            machine_id="prensa-hidraulica"
        )
    elif protocol == "opcua":
        data = opcua_data()
        return SimulatedDump(
            protocol="opcua",
            raw_dump=data["raw_dump"],
            machine_id="empaquetadora-01"
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unknown protocol: {protocol}")


@app.post("/api/translate", response_model=TranslateResponse)
async def translate(request: TranslateRequest):
    """
    Translate a raw industrial protocol dump to unified format.

    Supports:
    - Modbus TCP (registers, hex dumps)
    - S7comm Plus (Siemens S7-1500 optimized blocks)
    - OPC-UA (standard node structure)
    """
    t = get_translator()
    if t is None:
        return TranslateResponse(
            success=False,
            error="API key not configured. Set ANTHROPIC_API_KEY environment variable."
        )

    try:
        result = t.translate(request.raw_dump, request.machine_hint)
        return TranslateResponse(success=True, data=result.model_dump())
    except Exception as e:
        return TranslateResponse(success=False, error=str(e))


@app.post("/api/demo-translate")
async def demo_translate(request: TranslateRequest):
    """
    Demo translation endpoint - returns simulated AI response.
    Works without API key for demonstration purposes.
    """
    from datetime import datetime
    import random

    # Detect protocol from dump content
    raw = request.raw_dump.lower()

    if "modbus" in raw or "register" in raw or "0x4" in raw:
        protocol = "modbus"
        metrics = {
            "temperature_c": round(random.uniform(40, 80), 1),
            "rpm": random.randint(800, 1800),
            "status": random.choice(["running", "running", "running", "stopped"])
        }
        notes = "Decoded float from registers 40001-40002 (big-endian). Status word interpreted."
    elif "s7comm" in raw or "db_" in raw or "optimized" in raw:
        protocol = "s7comm"
        metrics = {
            "pressure_bar": round(random.uniform(2, 8), 2),
            "cycle_time_ms": random.randint(50, 200),
            "status": "running"
        }
        notes = "S7-1500 optimized block detected. Symbolic access parsed successfully."
    elif "opc" in raw or "ns=2" in raw:
        protocol = "opcua"
        metrics = {
            "piece_count": random.randint(10000, 50000),
            "efficiency_pct": round(random.uniform(75, 99), 1),
            "status": "running"
        }
        notes = "OPC-UA standard format. State enum mapped via EnumMapping."
    else:
        protocol = "unknown"
        metrics = {"status": "unknown"}
        notes = "Protocol not recognized. Please provide more context."

    result = {
        "machine_id": request.machine_hint or "unknown",
        "protocol_detected": protocol,
        "timestamp": datetime.now().isoformat(),
        "metrics": metrics,
        "alarms": [],
        "raw_confidence": round(random.uniform(0.85, 0.98), 2),
        "interpretation_notes": notes
    }

    return TranslateResponse(success=True, data=result)


if __name__ == "__main__":
    import uvicorn
    print("\n🚀 UniPLC Server starting...")
    print("   Dashboard: http://localhost:8000")
    print("   API Docs:  http://localhost:8000/docs\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
