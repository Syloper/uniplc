"""
S7comm Plus Simulator - Simulates S7-1500 with Optimized Data Blocks
Shows the pain point: no fixed addresses, symbolic access only, proprietary format
"""
import random
import base64
import json
from datetime import datetime


def generate_s7_optimized_block() -> dict:
    """
    Simulates an S7-1500 optimized data block.

    The pain point: addresses are NOT fixed (0x0000, 0x0004, etc.)
    Instead, we get symbolic names and the memory layout is dynamic.
    Traditional S7 drivers CAN'T read this without S7comm Plus.
    """
    pressure = random.uniform(1.5, 8.5)
    valve_open = random.choice([True, False])
    alarm_active = random.random() < 0.15
    cycle_time_ms = random.randint(50, 200)
    batch_id = random.randint(10000, 99999)

    # Simulate the optimized block structure (no fixed offsets!)
    return {
        "protocol": "s7comm_plus",
        "plc_model": "S7-1516-3 PN/DP",
        "firmware": "V2.9.4",
        "timestamp": datetime.now().isoformat(),
        "block_info": {
            "name": "DB_ProcessData",
            "number": 10,
            "type": "optimized",  # <-- THIS is the problem
            "symbolic_access_only": True
        },
        "variables": {
            "ProcessData.Pressure_Bar": {
                "value": pressure,
                "type": "Real",
                "offset": "dynamic"  # No fixed address!
            },
            "ProcessData.ValveStatus.MainValve": {
                "value": valve_open,
                "type": "Bool",
                "offset": "dynamic"
            },
            "ProcessData.Alarms.HighPressure": {
                "value": alarm_active,
                "type": "Bool",
                "offset": "dynamic"
            },
            "ProcessData.Performance.CycleTime": {
                "value": cycle_time_ms,
                "type": "Int",
                "offset": "dynamic"
            },
            "ProcessData.Production.CurrentBatch": {
                "value": batch_id,
                "type": "DInt",
                "offset": "dynamic"
            }
        }
    }


def generate_s7_raw_dump() -> str:
    """
    Generates what you'd see trying to read an optimized block
    with a traditional S7 driver (KEPServer, etc.) - FAILURE or garbage.

    Then shows what S7comm Plus returns (symbolic).
    """
    data = generate_s7_optimized_block()

    # Simulate the traditional driver failing
    traditional_attempt = """
--- Traditional S7 Driver Attempt (KEPServer) ---
Connecting to 192.168.1.100:102...
TSAP: 03.01
Reading DB10.DBD0 (4 bytes)...
ERROR: Access denied - Block uses optimized access
ERROR: Cannot determine memory layout
ERROR: Use symbolic addressing or OPC-UA server
----------------------------------------------
"""

    # Simulate S7comm Plus response (what works)
    s7plus_response = f"""
=== S7COMM PLUS RESPONSE ===
PLC: {data['plc_model']} (FW {data['firmware']})
Timestamp: {data['timestamp']}
Block: {data['block_info']['name']} (DB{data['block_info']['number']})
Access Mode: Symbolic (optimized block)

Variables Read:
"""
    for var_name, var_data in data["variables"].items():
        s7plus_response += f"  {var_name}: {var_data['value']} [{var_data['type']}]\n"

    s7plus_response += """
WARNING: Traditional addressing (DB10.DBD0) not available
NOTE: Requires TIA Portal export or S7comm Plus driver
=============================
"""

    return traditional_attempt + s7plus_response


def get_structured_data() -> dict:
    """Returns both raw dump and structured data for the demo."""
    data = generate_s7_optimized_block()
    return {
        "raw_dump": generate_s7_raw_dump(),
        "structured": data
    }


if __name__ == "__main__":
    print(generate_s7_raw_dump())
