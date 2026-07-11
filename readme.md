# ⚡ VESPERA: Local AI Operator Stack

Vespera is a hardened, fully local AI orchestration suite designed to embed powerful reasoning engines directly onto your lab environment. Outfitted with an automated deployment pipeline, dynamic hardware telemetry scanning, and an extensible persona architecture, Vespera bridges the gap between raw LLM weights and native local tooling (WSL, OSINT frameworks, and automation scripts).

![License](https://img.shields.io/badge/License-MIT-00FFC4?style=flat-flat)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20WSL-38BDF8?style=flat-flat)
![Engine](https://img.shields.io/badge/Backend-Ollama-A878FF?style=flat-flat)

---

## 🛠️ Core Features

* **Adaptive Hardware Telemetry Audit:** Automatically discovers your physical system RAM, queries discrete GPU VRAM registers, and maps out model quantization footprints on a real-time percentage compatibility scale to prevent Out-Of-Memory (OOM) crashes.
* **Multi-Engine Seamless Handoff:** Fully automated background compilation that dynamically builds backend templates and catch-all safety stop token profiles—allowing you to shift between `Gemma 3`, `Hermes 3`, `Llama 3.2`, or `Qwen` completely hands-off via the GUI.
* **Extensible Persona Arrays:** Decoupled runtime markdown configuration pipelines. Instantly swap active system personalities—from precise **Pure Logic** analytics to structured **OSINT / Recon Analysis** arrays—without leaving dual system prompt artifacts in your chat history.
* **Asynchronous Cyberpunk UI:** A responsive, multi-threaded WPF dashboard built to isolate heavy package downloading or model manifesting onto safe background runspaces, keeping the UI completely fluid during high-overhead processes.

---

## 📦 Directory Architecture

```text
Vespera/
├── app/
│   ├── setup/
│   │   ├── personas/                 # Modular .md profile templates
│   │   │   ├── pure_logic.md
│   │   │   └── osint_analyst.md
│   │   └── Install-Vespera-GUI.ps1   # Hardware scanner & WPF UI
│   ├── Install-Vespera.ps1           # Main environment compiler loop
│   └── Launch-UI.ps1                 # Local application dashboard
├── config/
│   └── operator.json                 # Active environment state array
├── Modelfile                         # Dynamically compiled Ollama map
├── START-GUI.bat                     # Entrypoint initialization script
└── Launch-Control-Center.bat         # Live production environment runner