# ⚡ VESPERA: Local AI Operator Stack

**Multi-OS (Python) is now the primary and recommended path.**

Vespera is a fully local, offline-first AI operator stack with hardware-aware model recommendations, modular cognitive personas, optional multi-agent (quad-brain) orchestration, and both web + pure-terminal interfaces.

The active development lives under the `multi_os/` directory on the `multi-os` branch.

![License](https://img.shields.io/badge/License-MIT-00FFC4?style=flat-flat)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-38BDF8?style=flat-flat)
![Engine](https://img.shields.io/badge/Backend-Ollama-A878FF?style=flat-flat)

---

## Primary Path: Multi-OS (Recommended)

Cross-platform Python rewrite supporting **Linux, macOS, and Windows**.

- Hardware prescan (RAM / VRAM / quantisation matrix)
- Modular personas (`pure_logic`, `osint_analyst` + multi-agent set)
- Sequential multi-agent pipeline (Strategist → Executor → Critic → Synthesizer)
- Gradio web Control Center + Textual pure-terminal TUI
- CLI: `scan`, `status`, `personas`, `chat`, `multi`, `ui`, `tui`, `tools`
- Optional packs: image/video generation, voice, local search, network diagnostics

### Quick Start (Multi-OS)

```bash
git clone https://github.com/vectisops/Vespera.git
cd Vespera
git checkout multi-os
cd multi_os

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m vespera scan
python -m vespera ui               # Web UI → http://127.0.0.1:7860
python -m vespera tui              # Pure terminal TUI
```

Full documentation, directory layout, tools, and roadmap:  
**→ [multi_os/README.md](multi_os/README.md)**

---

## Legacy: Original Windows-Only Beta

The original release was a Windows / PowerShell / WPF stack shipped as `VesperaV1-Beta.rar`.

It featured:
- Adaptive hardware telemetry audit and quantisation compatibility grid
- Automated backend compilation for multiple models (Gemma 3, Hermes 3, Llama 3.2, Qwen, etc.)
- Extensible markdown persona system
- Asynchronous WPF dashboard with background runspaces

### Legacy Structure (reference only)

```text
Vespera/
├── app/
│   ├── setup/
│   │   ├── personas/                 # Modular .md profile templates
│   │   └── Install-Vespera-GUI.ps1   # Hardware scanner & WPF UI
│   ├── Install-Vespera.ps1           # Main environment compiler loop
│   └── Launch-UI.ps1                 # Local application dashboard
├── config/
│   └── operator.json                 # Active environment state array
├── Modelfile                         # Dynamically compiled Ollama map
├── START-GUI.bat                     # Entrypoint initialization script
└── Launch-Control-Center.bat         # Live production environment runner
```

### Legacy Requirements
- Windows 10/11 (WSL2 optional for advanced tooling)
- Ollama local instance
- PowerShell execution permissions

The Multi-OS rewrite keeps the same conceptual flow (prescan → persona → model → Control Center) while making the entire stack portable. The RAR remains available for historical reference.

---

## License

MIT
