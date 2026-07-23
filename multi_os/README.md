# ⚡ VESPERA: Multi-OS Local AI Operator Stack

Cross-platform rewrite of the original Vespera (Windows / PowerShell / WPF) for **Linux, macOS, and Windows**.

A fully local, offline-first AI operator stack with modular cognitive personas, optional multi-agent (quad-brain) orchestration, hardware-aware model recommendations, and both web + pure-terminal UIs.

---

## Platform Support

| OS      | Status     | Notes                                      |
|---------|------------|--------------------------------------------|
| Linux   | ✅ Primary | Preferred for air-gapped / offline work    |
| macOS   | ✅ Full    | Metal acceleration via Ollama              |
| Windows | ✅ Full    | Native Python path; WSL2 optional          |

---

## Core Features

- **Hardware Prescan**  
  Cross-platform telemetry for system RAM, discrete GPU VRAM, and a conservative quantisation compatibility matrix. Includes lightweight matching for high-end mobile workstations (64 GB class + RTX 4090 Laptop). More aggressive machine-specific tuning lives in a private profile repo.

- **Modular Personas**  
  Drop-in markdown system prompts that can be swapped at runtime without residual prompt pollution:
  - `pure_logic`
  - `osint_analyst`
  - Multi-agent set: `strategist`, `executor`, `critic`, `synthesizer`

- **Multi-Agent Orchestration**  
  Sequential pipeline (Strategist → Executor → Critic → Synthesizer) that produces a clean synthesised final answer. Designed for later extension into persistent memory / continuity experiments.

- **Two UI modes**
  - Gradio web Control Center (browser)
  - Textual pure-terminal TUI (ideal for air-gapped / no-browser environments)

- **CLI surface**  
  `scan`, `status`, `personas`, `chat`, `multi`, `ui`, `tui`, `tools`

- **Ollama backend**  
  Official Python client + HTTP fallback. Fully local once models are present.

- **Optional capability packs** (graceful degradation if backends are missing)
  - Image generation (Automatic1111 / ComfyUI)
  - Video generation (ComfyUI workflows)
  - Voice (STT via faster-whisper / whisper.cpp, TTS via piper or Coqui)
  - Local search (SearXNG preferred, DuckDuckGo HTML fallback)
  - Network diagnostics (ping, DNS, routes, listeners — own-network use only)

---

## Quick Start

```bash
git clone https://github.com/vectisops/Vespera.git
cd Vespera
git checkout multi-os
cd multi_os

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Hardware check + quantisation advice
python -m vespera scan

# Web Control Center
python -m vespera ui
# → http://127.0.0.1:7860

# Pure terminal TUI (air-gapped)
python -m vespera tui

# One-shot chat
python -m vespera chat "Summarise the current risk picture"

# Multi-agent pipeline
python -m vespera multi "Design a resilient offline model serving strategy for a 16 GB VRAM laptop"
```

Linux helper script:
```bash
./scripts/launch.sh
```

Windows helper:
```powershell
.\scripts\launch.ps1
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
├── docs/
│   └── TOOLS.md
└── vespera/
    ├── hardware.py          # Cross-platform telemetry + profiles
    ├── agents.py            # Multi-agent (quad-brain) scaffold
    ├── config.py
    ├── ollama_client.py
    ├── cli.py
    ├── ui.py                # Gradio Control Center
    ├── tui.py               # Textual TUI
    ├── tools/               # Optional capability packs
    └── personas/
        ├── pure_logic.md
        ├── osint_analyst.md
        ├── strategist.md
        ├── executor.md
        ├── critic.md
        └── synthesizer.md
```

---

## Requirements

- Python 3.10+
- Ollama running locally (`http://127.0.0.1:11434` by default)
- Core packages listed in `requirements.txt`
- Optional: NVIDIA drivers + `nvidia-ml-py` for better VRAM reporting
- Optional backends for tools (A1111, ComfyUI, SearXNG, piper, faster-whisper, etc.) — see `docs/TOOLS.md`

---

## Migrating from the Original Windows Beta

The original `VesperaV1-Beta.rar` used PowerShell + WPF + `.bat` entry points.  
This rewrite keeps the same conceptual flow (prescan → persona → model → Control Center) but implements everything in portable Python.

Keep the RAR as historical reference; run the multi-OS tree side-by-side.

---

## Notes on Hardware Profiles

The public multi-OS code includes a lightweight matcher for high-end mobile workstations (64 GB system RAM + RTX 4090 Laptop class).  
Tighter, machine-specific advice lives in a private tailored repository and can be overlaid if desired.

---

## Roadmap (selected)

- Deeper multi-agent memory / continuity experiments
- Textual TUI polish + offline packaging
- PyInstaller / single-file binaries per OS
- Expanded AMD / Apple Silicon VRAM detection
- More robust tool registry and permission model

---

License: MIT
