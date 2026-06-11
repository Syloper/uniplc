"""
UniPLC AI Translator Agent
Uses LLM to interpret and normalize industrial protocol data
"""
import json
import os
from datetime import datetime
from typing import Optional

from anthropic import Anthropic
from pydantic import BaseModel


class UnifiedMetrics(BaseModel):
    """Unified output schema for all protocols"""
    machine_id: str
    protocol_detected: str
    timestamp: str
    metrics: dict
    alarms: list[str]
    raw_confidence: float
    interpretation_notes: Optional[str] = None


SYSTEM_PROMPT = """You are UniPLC, an industrial protocol translator AI. Your job is to:

1. DETECT which protocol the input data comes from (modbus, s7comm, opcua, or unknown)
2. PARSE the raw data, decoding hex values, interpreting registers, etc.
3. NORMALIZE to a unified JSON schema

## Protocol Recognition Hints:

**Modbus TCP:**
- Contains "MODBUS", register addresses like "40001", hex dumps
- Registers are 16-bit, floats span 2 registers (big-endian)
- Status words are bitmasks

**S7comm Plus (Siemens S7-1500):**
- Contains "S7COMM", "DB_" blocks, symbolic variable names
- May show errors about "optimized access"
- Variables have paths like "ProcessData.Pressure_Bar"

**OPC-UA:**
- Contains "OPC-UA", node IDs like "ns=2;s=..."
- Has DisplayName, DataType, Status fields
- May have EnumMapping for state values

## Output Schema:

Return ONLY valid JSON matching this structure:
{
  "machine_id": "string - derive from device ID, IP, or block name",
  "protocol_detected": "modbus|s7comm|opcua|unknown",
  "timestamp": "ISO8601 from the data, or current time if not present",
  "metrics": {
    "temperature_c": number or null,
    "pressure_bar": number or null,
    "rpm": number or null,
    "piece_count": number or null,
    "efficiency_pct": number or null,
    "cycle_time_ms": number or null,
    "status": "running|stopped|error|idle|maintenance|unknown"
  },
  "alarms": ["list of active alarms as strings"],
  "raw_confidence": 0.0-1.0,
  "interpretation_notes": "optional notes about parsing decisions"
}

## Parsing Rules:

For Modbus floats: Two consecutive 16-bit registers form a 32-bit float (big-endian).
Example: registers 0x4282, 0x88D3 → combine as bytes 42 82 88 D3 → float

For status words: 0x0001=Running, 0x0002=Stopped, 0x0004=Error (common convention)

For S7 booleans: true/True/1 = active

For OPC-UA enums: Use the EnumMapping if provided, otherwise use the raw value.

Always include interpretation_notes explaining any assumptions you made."""


class ProtocolTranslator:
    """AI-powered protocol translator using Claude"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    def translate(self, raw_dump: str, machine_hint: Optional[str] = None) -> UnifiedMetrics:
        """
        Translate raw protocol dump to unified schema.

        Args:
            raw_dump: Raw text dump from any industrial protocol
            machine_hint: Optional hint about machine identity

        Returns:
            UnifiedMetrics object with normalized data
        """
        user_message = f"Parse this industrial protocol dump and return unified JSON:\n\n{raw_dump}"

        if machine_hint:
            user_message += f"\n\nMachine hint: {machine_hint}"

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}]
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Try to parse JSON (handle markdown code blocks)
        json_str = response_text
        if "```json" in json_str:
            json_str = json_str.split("```json")[1].split("```")[0]
        elif "```" in json_str:
            json_str = json_str.split("```")[1].split("```")[0]

        data = json.loads(json_str.strip())

        return UnifiedMetrics(**data)

    def translate_batch(self, dumps: list[tuple[str, str]]) -> list[UnifiedMetrics]:
        """
        Translate multiple dumps.

        Args:
            dumps: List of (raw_dump, machine_hint) tuples

        Returns:
            List of UnifiedMetrics
        """
        results = []
        for raw_dump, hint in dumps:
            try:
                result = self.translate(raw_dump, hint)
                results.append(result)
            except Exception as e:
                # Return a failed result
                results.append(UnifiedMetrics(
                    machine_id=hint or "unknown",
                    protocol_detected="unknown",
                    timestamp=datetime.now().isoformat(),
                    metrics={},
                    alarms=[f"Translation error: {str(e)}"],
                    raw_confidence=0.0,
                    interpretation_notes=f"Failed to parse: {str(e)}"
                ))
        return results


def translate_dump(raw_dump: str, machine_hint: Optional[str] = None) -> dict:
    """
    Convenience function to translate a single dump.
    Returns dict instead of Pydantic model for easier JSON serialization.
    """
    translator = ProtocolTranslator()
    result = translator.translate(raw_dump, machine_hint)
    return result.model_dump()


if __name__ == "__main__":
    # Test with a sample Modbus dump
    test_dump = """
=== MODBUS TCP CAPTURE ===
Timestamp: 2024-03-15T10:30:00
Device: Slave ID 1
Function: 03 (Read Holding Registers)
Start: 40001, Count: 6

Raw Response: 01 03 0C 4282 88D3 44CE 0858 0001 0000

Register Dump:
  40001: 0x4282
  40002: 0x88D3
  40003: 0x44CE
  40004: 0x0858
  40005: 0x0001
  40006: 0x0000
===========================
"""
    result = translate_dump(test_dump, "linea-1-fresadora")
    print(json.dumps(result, indent=2, ensure_ascii=False))
