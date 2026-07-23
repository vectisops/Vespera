"""
Textual TUI Control Center for Vespera.
Designed for air-gapped / pure-terminal environments where a browser UI is undesirable.
"""

from __future__ import annotations

from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Header, Footer, Static, Input, Button, Select, RichLog, Label, TabbedContent, TabPane
)
from textual.binding import Binding
from rich.panel import Panel
from rich.markdown import Markdown

from .config import load_config, save_config, list_personas, load_persona
from .hardware import scan_hardware
from .ollama_client import OllamaClient
from .agents import MultiAgentOrchestrator


class VesperaTUI(App):
    """Air-gapped friendly Control Center."""

    CSS = """
    Screen {
        background: #0c0c0c;
    }
    Header {
        background: #111;
        color: #00ffc4;
    }
    Footer {
        background: #111;
    }
    #chat_log {
        height: 1fr;
        border: solid #333;
        background: #111;
    }
    #input_row {
        height: auto;
        padding: 1;
    }
    #status {
        height: auto;
        border: solid #222;
        padding: 1;
        color: #aaa;
    }
    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("ctrl+l", "clear_chat", "Clear"),
        Binding("f5", "refresh_hw", "Refresh HW"),
    ]

    def __init__(self):
        super().__init__()
        self.cfg = load_config()
        self.client = OllamaClient(self.cfg.get("ollama_host", "http://127.0.0.1:11434"))
        self.history: List[tuple[str, str]] = []
        self.persona_names = list(list_personas().keys()) or ["pure_logic"]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Chat", id="tab-chat"):
                yield RichLog(id="chat_log", markup=True, highlight=True, wrap=True)
                with Horizontal(id="input_row"):
                    yield Select(
                        [(p, p) for p in self.persona_names],
                        value=self.cfg.get("active_persona", self.persona_names[0]),
                        id="persona_select",
                        allow_blank=False,
                    )
                    yield Input(placeholder="Message Vespera…", id="chat_input")
                    yield Button("Send", id="send_btn", variant="primary")
                    yield Button("Multi-Agent", id="multi_btn", variant="success")
            with TabPane("Hardware", id="tab-hw"):
                yield Static(id="hw_panel")
            with TabPane("Status", id="tab-status"):
                yield Static(id="status_panel")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "Vespera TUI"
        self.sub_title = "Multi-OS Local AI Operator"
        self.action_refresh_hw()
        self._refresh_status()
        self.query_one("#chat_input", Input).focus()

    def action_clear_chat(self) -> None:
        self.history.clear()
        log = self.query_one("#chat_log", RichLog)
        log.clear()

    def action_refresh_hw(self) -> None:
        report = scan_hardware()
        d = report.to_dict()
        lines = [
            f"[bold cyan]OS[/]  {d['os']} ({d['arch']})",
            f"[bold cyan]CPU[/] {d['cpu']['physical']}c / {d['cpu']['logical']}t",
            f"[bold cyan]RAM[/] {d['ram_gb']['total']} GB total  |  {d['ram_gb']['available']} GB free",
        ]
        if d["gpus"]:
            for g in d["gpus"]:
                lines.append(
                    f"[bold cyan]GPU[/] {g['name']}  |  {g['total_vram_mb']/1024:.1f} GB  "
                    f"({g['free_vram_mb']/1024:.1f} free)"
                )
        else:
            lines.append("[bold cyan]GPU[/] None detected")
        if d.get("profile"):
            lines.append(f"[bold green]Profile[/] {d['profile']}")
        rec = d["recommendation_12b"]
        lines.append(f"[bold yellow]12B advice[/] {rec['recommended']}  (budget ~{rec['budget_gb']} GB)")
        for n in d.get("notes", []):
            lines.append(f"[dim]• {n}[/]")
        self.query_one("#hw_panel", Static).update("\n".join(lines))

    def _refresh_status(self) -> None:
        ok = self.client.is_available()
        models = []
        if ok:
            try:
                models = [m.get("name") or m.get("model") for m in self.client.list_models()]
            except Exception:
                pass
        text = (
            f"Ollama: {'[green]reachable[/]' if ok else '[red]offline[/]'}\n"
            f"Active persona: {self.cfg.get('active_persona')}\n"
            f"Default model: {self.cfg.get('default_model')}\n"
            f"Models: {', '.join(m for m in models if m)[:120] or 'none'}"
        )
        self.query_one("#status_panel", Static).update(text)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_btn":
            await self._do_chat(multi=False)
        elif event.button.id == "multi_btn":
            await self._do_chat(multi=True)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "chat_input":
            await self._do_chat(multi=False)

    async def _do_chat(self, multi: bool = False) -> None:
        inp = self.query_one("#chat_input", Input)
        msg = inp.value.strip()
        if not msg:
            return
        inp.value = ""

        persona_sel = self.query_one("#persona_select", Select)
        persona = str(persona_sel.value) if persona_sel.value else self.cfg.get("active_persona", "pure_logic")

        log = self.query_one("#chat_log", RichLog)
        log.write(f"[bold cyan]You[/]\n{msg}\n")

        model = self.cfg.get("default_model", "gemma3:12b")

        if not self.client.is_available():
            log.write("[red]Ollama is not reachable. Start `ollama serve` first.[/]\n")
            return

        if multi:
            log.write("[dim]Running sequential multi-agent (Strategist → Executor → Critic → Synthesizer)…[/]\n")
            orch = MultiAgentOrchestrator(client=self.client, model=model)
            result = orch.run_sequential(msg)
            for t in result.turns:
                log.write(f"[bold yellow]{t.agent.upper()}[/]\n{t.content}\n")
            log.write(f"[bold green]FINAL (Synthesizer)[/]\n{result.final}\n")
            self.history.append((msg, result.final))
        else:
            try:
                system = load_persona(persona)
            except Exception as e:
                log.write(f"[red]Persona error: {e}[/]\n")
                return
            messages = [{"role": "system", "content": system}]
            for u, a in self.history[-6:]:
                messages.append({"role": "user", "content": u})
                messages.append({"role": "assistant", "content": a})
            messages.append({"role": "user", "content": msg})

            try:
                resp = self.client.chat(model=model, messages=messages, stream=False)
                if isinstance(resp, dict):
                    content = resp.get("message", {}).get("content") or resp.get("response") or str(resp)
                else:
                    content = str(resp)
            except Exception as e:
                content = f"Error: {e}"

            log.write(f"[bold green]Vespera ({persona})[/]\n{content}\n")
            self.history.append((msg, content))


def main():
    app = VesperaTUI()
    app.run()


if __name__ == "__main__":
    main()
