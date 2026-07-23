# ⚡ VESPERA: Multi-OS Local AI Operator Stack

Cross-platform rewrite of the original Vespera (Windows / PowerShell / WPF) for **Linux, macOS, and Windows**.

Built for sovereign, offline, high-performance local AI operation with modular cognitive personas and an optional multi-agent (quad-brain) orchestration layer.

---

## Platform Support

| OS      | Status            | Notes |
|---------|-------------------|-------|
| Linux   | ✅ Primary        | Preferred for sovereign / air-gapped work |
| macOS   | ✅ Full           | Metal via Ollama |
| Windows | ✅ Full           | Native Python path; WSL2 optional |

---

## Features

- **Hardware Prescan** – RAM / VRAM / conservative quantisation matrix. Optional known-machine profiles (e.g. high-end mobile workstations with RTX 4090 Laptop class).
- **Modular Personas** – Drop-in markdown system prompts:
  - `pure_logic`, `osint_analyst`, `tactical_ops`
  - Multi-agent set: `strategist`, `executor`, `critic`, `synthesizer`
- **Multi-Agent Orchestration** – Sequential pipeline (Strategist → Executor → Critic → Synthesizer) with clean synthesis of a unified answer.
- **Two UI modes**:
  - Gradio web Control Center (browser)
  - Textual pure-terminal TUI (ideal for air-gapped / no-browser environments)
- **CLI** – `scan`, `status`, `personas`, `chat`, `multi`, `ui`, `tui`
- **Ollama backend** – Official client + HTTP fallback. Fully local after models are present.

---

## Quick Start

```bash
cd multi_os
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Hardware check
python -m vespera scan

# Web UI
python -m vespera ui
# → http://127.0.0.1:7860

# Pure terminal TUI (air-gapped)
python -m vespera tui

# One-shot chat
python -m vespera chat "Summarise the current risk picture"

# Multi-agent pipeline
python -m vespera multi "Design a resilient offline model serving strategy for a 16 GB VRAM laptop"
```

Linux helper:
```bash
./scripts/launch.sh
```

---

## Directory Layout

```text
multi_os/
├── README.md
├── requirements.txt
├── scripts/
│   ├── launch.sh
│   └── launch.ps1
└── vespera/
    ├── hardware.py          # Cross-platform telemetry + profiles
    ├── agents.py            # Multi-agent (quad-brain) scaffold
    ├── config.py
    ├── ollama_client.py
    ├── cli.py
    ├── ui.py                # Gradio
    ├── tui.py               # Textual
    └── personas/
        ├── pure_logic.md
        ├── osint_analyst.md
        ├── tactical_ops.md
        ├── strategist.md
        ├── executor.md
        ├── critic.md
        └── synthesizer.md
```

---

## Migrating from the Original Windows Beta

The original `VesperaV1-Beta.rar` used PowerShell + WPF + `.bat`.  
This rewrite keeps the same conceptual flow (prescan → persona → model → Control Center) but implements everything in portable Python.

Keep the RAR as reference; run the multi-OS tree side-by-side.

---

## Notes on Hardware Profiles

Public multi-OS code includes a lightweight matcher for high-end mobile workstations (64 GB class + RTX 4090 Laptop).  
More aggressive, machine-specific tuning lives in a private tailored branch/repo.

---

## Roadmap (selected)

- Deeper multi-agent memory / continuity / “digital child” experiments
- Textual TUI polish + offline packaging
- PyInstaller / single-file binaries per OS
- Expanded AMD / Apple Silicon VRAM detection

License: MIT
