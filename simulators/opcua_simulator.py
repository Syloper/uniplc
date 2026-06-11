"""
OPC-UA Simulator - Simulates a generic PLC with standard OPC-UA
This is the "ideal" case but still has its own format quirks
"""
import random
import uuid
from datetime import datetime


def generate_opcua_nodes() -> dict:
    """
    Simulates OPC-UA node structure from a generic PLC.
    OPC-UA is more standardized but still has vendor-specific quirks.
    """
    piece_count = random.randint(1000, 50000)
    efficiency = random.uniform(75.0, 99.5)
    machine_state = random.choice([1, 2, 3, 4, 5])  # OPC-UA often uses enums
    last_maintenance = "2024-01-15T08:30:00Z"
    motor_temp = random.uniform(40.0, 75.0)

    # Map state codes to meanings (vendor-specific!)
    state_map = {
        1: "Idle",
        2: "Running",
        3: "Paused",
        4: "Maintenance",
        5: "Fault"
    }

    return {
        "protocol": "opcua",
        "server_uri": "opc.tcp://192.168.1.50:4840",
        "namespace": "http://genericplc.com/UA/",
        "timestamp": datetime.now().isoformat(),
        "nodes": [
            {
                "node_id": "ns=2;s=Production.Counter.TotalPieces",
                "display_name": "Total Pieces",
                "value": piece_count,
                "data_type": "UInt32",
                "source_timestamp": datetime.now().isoformat(),
                "status": "Good"
            },
            {
                "node_id": "ns=2;s=Production.Efficiency.OEE",
                "display_name": "Overall Equipment Effectiveness",
                "value": efficiency,
                "data_type": "Double",
                "source_timestamp": datetime.now().isoformat(),
                "status": "Good"
            },
            {
                "node_id": "ns=2;s=Machine.State.Current",
                "display_name": "Machine State",
                "value": machine_state,
                "data_type": "Int16",
                "source_timestamp": datetime.now().isoformat(),
                "status": "Good",
                "enum_values": state_map
            },
            {
                "node_id": "ns=2;s=Maintenance.LastService",
                "display_name": "Last Maintenance Date",
                "value": last_maintenance,
                "data_type": "DateTime",
                "source_timestamp": datetime.now().isoformat(),
                "status": "Good"
            },
            {
                "node_id": "ns=2;s=Motors.Main.Temperature",
                "display_name": "Main Motor Temperature",
                "value": motor_temp,
                "data_type": "Float",
                "source_timestamp": datetime.now().isoformat(),
                "status": "Good",
                "engineering_units": "°C"
            }
        ]
    }


def generate_opcua_dump() -> str:
    """
    Generates an OPC-UA browse/read dump.
    """
    data = generate_opcua_nodes()

    dump = f"""
=== OPC-UA CLIENT RESPONSE ===
Server: {data['server_uri']}
Namespace: {data['namespace']}
Timestamp: {data['timestamp']}

Browse Result (ns=2):
"""
    for node in data["nodes"]:
        dump += f"""
  Node: {node['node_id']}
    DisplayName: {node['display_name']}
    Value: {node['value']}
    DataType: {node['data_type']}
    Status: {node['status']}
    SourceTimestamp: {node['source_timestamp']}
"""
        if "engineering_units" in node:
            dump += f"    Units: {node['engineering_units']}\n"
        if "enum_values" in node:
            dump += f"    EnumMapping: {node['enum_values']}\n"

    dump += """
==============================
"""
    return dump


def get_structured_data() -> dict:
    """Returns both raw dump and structured data for the demo."""
    data = generate_opcua_nodes()
    return {
        "raw_dump": generate_opcua_dump(),
        "structured": data
    }


if __name__ == "__main__":
    print(generate_opcua_dump())
