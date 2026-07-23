"""Command-line interface for Vespera multi-OS."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .config import load_config, save_config, list_personas, load_persona
from .hardware import scan_hardware, print_report
from .ollama_client import OllamaClient
from .agents import MultiAgentOrchestrator

app = typer.Typer(
    name="vespera",
    help="Vespera Multi-OS Local AI Operator Stack",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version."""
    console.print(f"Vespera multi-OS [bold cyan]{__version__}[/]")


@app.command()
def scan():
    """Run hardware prescan and print compatibility matrix."""
    print_report()


@app.command()
def personas():
    """List available cognitive personas."""
    ps = list_personas()
    table = Table(title="Available Personas")
    table.add_column("Name", style="cyan")
    table.add_column("Path")
    for name, path in sorted(ps.items()):
        table.add_row(name, str(path))
    console.print(table)


@app.command()
def status():
    """Show current config + Ollama status + quick hardware summary."""
    cfg = load_config()
    client = OllamaClient(cfg.get("ollama_host", "http://127.0.0.1:11434"))

    console.print(Panel.fit(
        f"[bold]Active persona:[/] {cfg.get('active_persona')}\n"
        f"[bold]Default model:[/] {cfg.get('default_model')}\n"
        f"[bold]Ollama host:[/] {cfg.get('ollama_host')}"
    ))

    if client.is_available():
        models = client.list_models()
        console.print(f"[green]Ollama is reachable[/] – {len(models)} model(s) present")
        for m in models[:10]:
            name = m.get("name") or m.get("model") or str(m)
            console.print(f"  • {name}")
    else:
        console.print("[red]Ollama is not reachable[/] at the configured host.")

    report = scan_hardware()
    console.print(
        f"\n[dim]Quick hardware:[/] {report.total_ram_gb:.0f} GB RAM  |  "
        f"{len(report.gpus)} NVIDIA GPU(s)"
        + (f"  |  Profile: {report.profile_name}" if report.profile_name else "")
    )


@app.command()
def set_persona(name: str):
    """Set the active persona."""
    available = list_personas()
    if name not in available:
        console.print(f"[red]Unknown persona '{name}'. Available: {list(available.keys())}[/]")
        raise typer.Exit(1)
    cfg = load_config()
    cfg["active_persona"] = name
    save_config(cfg)
    console.print(f"[green]Active persona set to[/] [cyan]{name}[/]")


@app.command()
def chat(
    message: str = typer.Argument(..., help="Your message"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
    persona: Optional[str] = typer.Option(None, "--persona", "-p"),
):
    """Quick one-shot chat using the active persona + model."""
    cfg = load_config()
    model = model or cfg.get("default_model", "gemma3:12b")
    persona_name = persona or cfg.get("active_persona", "pure_logic")

    try:
        system_prompt = load_persona(persona_name)
    except FileNotFoundError as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(1)

    client = OllamaClient(cfg.get("ollama_host", "http://127.0.0.1:11434"))
    if not client.is_available():
        console.print("[red]Ollama is not running or not reachable.[/]")
        raise typer.Exit(1)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message},
    ]

    console.print(f"[dim]Persona: {persona_name}  |  Model: {model}[/]\n")
    with console.status("Thinking…"):
        resp = client.chat(model=model, messages=messages, stream=False)

    if isinstance(resp, dict):
        content = resp.get("message", {}).get("content") or resp.get("response") or str(resp)
    else:
        content = str(resp)

    console.print(Panel(content, title="Vespera", border_style="cyan"))


@app.command("multi")
def multi_agent(
    message: str = typer.Argument(..., help="Your message"),
    model: Optional[str] = typer.Option(None, "--model", "-m"),
):
    """Run the sequential multi-agent pipeline (Strategist → Executor → Critic → Synthesizer)."""
    cfg = load_config()
    model = model or cfg.get("default_model", "gemma3:12b")
    client = OllamaClient(cfg.get("ollama_host", "http://127.0.0.1:11434"))
    if not client.is_available():
        console.print("[red]Ollama is not reachable.[/]")
        raise typer.Exit(1)

    console.print(f"[dim]Multi-agent mode  |  Model: {model}[/]\n")
    orch = MultiAgentOrchestrator(client=client, model=model)
    with console.status("Running agent pipeline…"):
        result = orch.run_sequential(message)

    for t in result.turns:
        console.print(Panel(t.content, title=t.agent.upper(), border_style="yellow"))
    console.print(Panel(result.final, title="FINAL (Synthesizer)", border_style="green"))


@app.command()
def ui():
    """Launch the Gradio web Control Center."""
    from .ui import main as ui_main
    ui_main()


@app.command()
def tui():
    """Launch the pure-terminal Textual TUI (air-gapped friendly)."""
    from .tui import main as tui_main
    tui_main()


def main():
    app()


if __name__ == "__main__":
    main()
