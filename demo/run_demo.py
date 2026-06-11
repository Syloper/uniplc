#!/usr/bin/env python3
"""
UniPLC Demo - Shows AI protocol translation in action
"""
import json
import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich import print as rprint

from simulators.modbus_simulator import generate_modbus_dump
from simulators.s7comm_simulator import generate_s7_raw_dump
from simulators.opcua_simulator import generate_opcua_dump
from agent.translator import ProtocolTranslator


console = Console()


def print_header():
    console.print(Panel.fit(
        "[bold blue]UniPLC[/bold blue] - Universal Protocol Translator\n"
        "[dim]AI-powered industrial protocol unification for SMEs[/dim]",
        border_style="blue"
    ))
    console.print()


def print_raw_dump(title: str, dump: str, protocol: str):
    """Display raw protocol dump"""
    console.print(f"\n[bold yellow]📡 {title}[/bold yellow]")
    console.print(f"[dim]Protocol: {protocol}[/dim]\n")
    console.print(Panel(dump.strip(), border_style="dim"))


def print_unified_result(result: dict):
    """Display unified result in a nice table"""
    table = Table(title="Unified Output", show_header=True, header_style="bold green")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Machine ID", result.get("machine_id", "unknown"))
    table.add_row("Protocol Detected", result.get("protocol_detected", "unknown"))
    table.add_row("Timestamp", result.get("timestamp", "N/A"))
    table.add_row("Confidence", f"{result.get('raw_confidence', 0):.0%}")

    console.print(table)

    # Metrics
    metrics = result.get("metrics", {})
    if metrics:
        mtable = Table(title="Metrics", show_header=True, header_style="bold cyan")
        mtable.add_column("Metric", style="white")
        mtable.add_column("Value", style="green")

        for key, value in metrics.items():
            if value is not None:
                mtable.add_row(key, str(value))

        console.print(mtable)

    # Alarms
    alarms = result.get("alarms", [])
    if alarms:
        console.print(f"\n[bold red]🚨 Alarms:[/bold red]")
        for alarm in alarms:
            console.print(f"  • {alarm}")

    # Notes
    notes = result.get("interpretation_notes")
    if notes:
        console.print(f"\n[dim]📝 Notes: {notes}[/dim]")


def run_demo():
    """Run the full demo"""
    print_header()

    console.print("[bold]This demo shows how UniPLC translates 3 different protocols into a unified format.[/bold]\n")
    console.print("Simulating data from:")
    console.print("  1. [cyan]S7-300 (Legacy)[/cyan] → Modbus TCP")
    console.print("  2. [cyan]S7-1500 (Modern)[/cyan] → S7comm Plus with optimized blocks")
    console.print("  3. [cyan]Generic PLC[/cyan] → OPC-UA\n")

    input("[dim]Press Enter to start...[/dim]")

    # Initialize translator
    console.print("\n[bold blue]Initializing AI Translator...[/bold blue]")
    try:
        translator = ProtocolTranslator()
    except Exception as e:
        console.print(f"[bold red]Error: Could not initialize translator.[/bold red]")
        console.print(f"[dim]Make sure ANTHROPIC_API_KEY is set.[/dim]")
        console.print(f"[dim]Error: {e}[/dim]")
        return

    # Demo data
    machines = [
        ("Fresadora Línea 1 (S7-300)", generate_modbus_dump(), "modbus", "linea1-fresadora"),
        ("Prensa Hidráulica (S7-1500)", generate_s7_raw_dump(), "s7comm", "prensa-hidraulica"),
        ("Empaquetadora (PLC Genérico)", generate_opcua_dump(), "opcua", "empaquetadora-01"),
    ]

    results = []

    for name, raw_dump, protocol, machine_id in machines:
        console.print(f"\n{'='*60}")
        print_raw_dump(name, raw_dump, protocol)

        console.print(f"\n[bold blue]🤖 AI Translating...[/bold blue]")

        try:
            result = translator.translate(raw_dump, machine_id)
            result_dict = result.model_dump()
            results.append(result_dict)

            console.print("[bold green]✓ Translation complete[/bold green]\n")
            print_unified_result(result_dict)

        except Exception as e:
            console.print(f"[bold red]✗ Translation failed: {e}[/bold red]")

        input("\n[dim]Press Enter for next machine...[/dim]")

    # Final summary
    console.print(f"\n{'='*60}")
    console.print(Panel.fit(
        "[bold green]Demo Complete![/bold green]\n\n"
        f"Translated [bold]{len(results)}[/bold] different protocols into unified format.\n"
        "This is what UniPLC does: eliminates integration complexity for industrial SMEs.",
        border_style="green"
    ))

    # Show all results as JSON
    console.print("\n[bold]Full JSON Output:[/bold]")
    console.print(Syntax(json.dumps(results, indent=2, ensure_ascii=False), "json", theme="monokai"))


def run_quick_demo():
    """Run a quick non-interactive demo (for testing)"""
    print_header()

    translator = ProtocolTranslator()

    machines = [
        ("Modbus S7-300", generate_modbus_dump(), "linea1"),
        ("S7comm S7-1500", generate_s7_raw_dump(), "prensa"),
        ("OPC-UA Generic", generate_opcua_dump(), "empaq"),
    ]

    results = []
    for name, dump, hint in machines:
        console.print(f"\n[bold]{name}[/bold]")
        result = translator.translate(dump, hint)
        results.append(result.model_dump())
        console.print(f"  → {result.protocol_detected} | {result.metrics.get('status', 'N/A')} | confidence: {result.raw_confidence:.0%}")

    return results


if __name__ == "__main__":
    if "--quick" in sys.argv:
        run_quick_demo()
    else:
        run_demo()
