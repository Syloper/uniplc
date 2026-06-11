"""
Modbus TCP Simulator - Simulates S7-300 legacy PLC
Outputs raw Modbus register data as hex dumps
"""
import random
import struct
import time
from datetime import datetime


def generate_modbus_registers() -> dict:
    """
    Simulates reading Modbus holding registers from an S7-300.
    Returns raw register data as it would come from pymodbus.

    Register map (simulated):
    - 40001-40002: Temperature (float, 2 registers)
    - 40003-40004: RPM (float, 2 registers)
    - 40005: Status word (uint16)
    - 40006: Error code (uint16)
    """
    temp = random.uniform(35.0, 85.0)
    rpm = random.uniform(800, 1800)
    status = random.choice([0x0001, 0x0002, 0x0004])  # Running, Stopped, Error
    error_code = 0 if status != 0x0004 else random.randint(100, 999)

    # Pack floats into 2x uint16 (big-endian, as Modbus does)
    temp_bytes = struct.pack('>f', temp)
    rpm_bytes = struct.pack('>f', rpm)

    temp_regs = struct.unpack('>HH', temp_bytes)
    rpm_regs = struct.unpack('>HH', rpm_bytes)

    return {
        "protocol": "modbus_tcp",
        "device_id": 1,
        "timestamp": datetime.now().isoformat(),
        "registers": {
            "40001": temp_regs[0],
            "40002": temp_regs[1],
            "40003": rpm_regs[0],
            "40004": rpm_regs[1],
            "40005": status,
            "40006": error_code
        },
        "raw_hex": f"01 03 0C {temp_regs[0]:04X} {temp_regs[1]:04X} {rpm_regs[0]:04X} {rpm_regs[1]:04X} {status:04X} {error_code:04X}"
    }


def generate_modbus_dump() -> str:
    """
    Generates a raw Modbus dump as a string, simulating what you'd capture
    from a network sniffer or low-level read.
    """
    data = generate_modbus_registers()

    # Format as a realistic dump that an integrator might see
    dump = f"""
=== MODBUS TCP CAPTURE ===
Timestamp: {data['timestamp']}
Device: Slave ID {data['device_id']}
Function: 03 (Read Holding Registers)
Start: 40001, Count: 6

Raw Response: {data['raw_hex']}

Register Dump:
  40001: 0x{data['registers']['40001']:04X}
  40002: 0x{data['registers']['40002']:04X}
  40003: 0x{data['registers']['40003']:04X}
  40004: 0x{data['registers']['40004']:04X}
  40005: 0x{data['registers']['40005']:04X}
  40006: 0x{data['registers']['40006']:04X}
===========================
"""
    return dump


def get_structured_data() -> dict:
    """Returns both raw dump and structured data for the demo."""
    data = generate_modbus_registers()
    return {
        "raw_dump": generate_modbus_dump(),
        "structured": data
    }


if __name__ == "__main__":
    print(generate_modbus_dump())
