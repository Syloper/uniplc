# UniPLC - Universal Protocol Translator

> AI-powered industrial protocol unification for SMEs

## The Problem

Industrial SMEs have machines from different eras and manufacturers:
- **Legacy PLCs** (S7-300) speaking Modbus with raw hex registers
- **Modern PLCs** (S7-1500) with proprietary optimized blocks
- **Generic PLCs** with OPC-UA but vendor-specific quirks

Integrating these requires expensive SCADA systems, Siemens licenses, and weeks of configuration.

## The Solution

UniPLC uses AI to **automatically detect, parse, and normalize** data from any industrial protocol into a unified schema — no manual configuration required.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  S7-300     │     │  S7-1500    │     │  Generic    │
│  (Modbus)   │     │  (S7comm+)  │     │  (OPC-UA)   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   UniPLC    │
                    │   AI Agent  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Unified    │
                    │   Schema    │
                    └─────────────┘
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your API key

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run the demo

```bash
python demo/run_demo.py
```

Or quick mode (non-interactive):

```bash
python demo/run_demo.py --quick
```

### 4. Run the API server

```bash
python api/main.py
# → http://localhost:8000
```

## API Usage

```bash
curl -X POST http://localhost:8000/translate \
  -H "Content-Type: application/json" \
  -d '{
    "raw_dump": "=== MODBUS TCP CAPTURE ===\n...",
    "machine_hint": "fresadora-linea-1"
  }'
```

## Unified Output Schema

All protocols are normalized to:

```json
{
  "machine_id": "fresadora-linea-1",
  "protocol_detected": "modbus",
  "timestamp": "2024-03-15T10:30:00",
  "metrics": {
    "temperature_c": 65.2,
    "pressure_bar": null,
    "rpm": 1456,
    "piece_count": null,
    "efficiency_pct": null,
    "cycle_time_ms": null,
    "status": "running"
  },
  "alarms": [],
  "raw_confidence": 0.95,
  "interpretation_notes": "Decoded float from registers 40001-40002"
}
```

## Project Structure

```
uia/
├── simulators/          # Fake data generators for each protocol
│   ├── modbus_simulator.py
│   ├── s7comm_simulator.py
│   └── opcua_simulator.py
├── agent/               # AI translation engine
│   └── translator.py
├── api/                 # REST API
│   └── main.py
├── demo/                # Interactive demo
│   └── run_demo.py
└── requirements.txt
```

## What This POC Demonstrates

1. **Protocol Detection**: AI recognizes Modbus, S7comm, OPC-UA automatically
2. **Data Parsing**: Decodes hex registers, interprets symbolic variables
3. **Schema Normalization**: Outputs consistent JSON regardless of source
4. **Zero Config**: No manual mapping or protocol configuration needed

## Next Steps (Production)

- [ ] Real protocol adapters (pymodbus, python-snap7, opcua-asyncio)
- [ ] WebSocket streaming for real-time data
- [ ] Historical data storage (TimescaleDB)
- [ ] Alert engine with ML anomaly detection
- [ ] Dashboard UI (React + charts)

## License

MIT
