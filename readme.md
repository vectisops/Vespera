# ⚡ VESPERA — Local AI Operator Stack

Fully local, offline-first AI operator stack with hardware-aware model recommendations, modular cognitive personas, optional multi-agent (quad-brain) orchestration, and both browser + pure-terminal interfaces.

**Current primary path: Multi-OS Python** (Linux / macOS / Windows) on the `multi-os` branch.

![License](https://img.shields.io/badge/License-MIT-00FFC4?style=flat-flat)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-38BDF8?style=flat-flat)
![Backend](https://img.shields.io/badge/Backend-Ollama-A878FF?style=flat-flat)

---

## Project Structure (as of July 2026)

| Component | Status | Location |
|-----------|--------|----------|
| **Multi-OS (Python)** | Active / Primary | `multi-os` branch → `multi_os/` |
| **Legacy Windows Beta** | Archived reference | `main` branch → `VesperaV1-Beta.rar` + original PowerShell/WPF files |
| **Mobile / APK track** | Early / planning | See `Vespera_Mobile_Vision_Upgrade_Dossier.pdf` (future dedicated `apk` branch) |

The Multi-OS rewrite keeps the original conceptual flow (hardware prescan → persona selection → model → Control Center) while making everything portable in pure Python.

---

## 1. Multi-OS (Recommended)

Cross-platform Python operator stack.

### Features
- Hardware prescan (system RAM, discrete GPU VRAM, conservative quantisation matrix)
- Modular personas (`pure_logic`, `osint_analyst` + multi-agent set: strategist / executor / critic / synthesizer)
- Sequential multi-agent pipeline that produces a clean synthesised answer
- Gradio web Control Center + Textual pure-terminal TUI
- CLI: `scan`, `status`, `personas`, `chat`, `multi`, `ui`, `tui`, `tools`
- Optional capability packs (image/video gen, voice STT/TTS, local search, network diagnostics) — graceful if backends missing
- Ollama backend (official client + HTTP fallback)

### Quick start (all platforms)

```bash
git clone https://github.com/vectisops/Vespera.git
cd Vespera
git checkout multi-os
cd multi_os

python -m venv .venv
# Linux / macOS:
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt

python -m vespera scan          # hardware + quant advice
python -m vespera ui            # web Control Center → http://127.0.0.1:7860
python -m vespera tui           # pure terminal TUI (air-gapped friendly)
```

Full details, tools, directory layout and roadmap:  
**[multi_os/README.md](https://github.com/vectisops/Vespera/blob/multi-os/multi_os/README.md)**

---

### Short OS guides

#### Linux
```bash
# After clone + checkout multi-os + cd multi_os
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Optional helper
./scripts/launch.sh

# Preferred environment for air-gapped / offline work
python -m vespera tui
```
Requires: Python 3.10+, Ollama installed and running, optional `nvidia-ml-py` for better VRAM reporting.

#### macOS
```bash
# After clone + checkout multi-os + cd multi_os
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python -m vespera scan
python -m vespera ui
```
Ollama uses Metal acceleration automatically. Same Python requirements as Linux.

#### Windows
```powershell
# After clone + checkout multi-os + cd multi_os
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python -m vespera scan
python -m vespera ui

# Optional helper
.\scripts\launch.ps1
```
Native Python path works; WSL2 is optional for extra tooling. PowerShell execution policy may need adjusting for the helper script.

---

## 2. Legacy Windows-Only Beta

The original release (July 2026) was a Windows / PowerShell / WPF stack distributed as `VesperaV1-Beta.rar`.

It provided:
- Adaptive hardware telemetry + quantisation compatibility grid
- Automated backend compilation for multiple models
- Extensible markdown persona system
- Asynchronous WPF dashboard

**Still available on this (`main`) branch for historical reference.**  
Double-click `START HERE - Install Vespera.bat` (or the RAR contents) if you specifically need the old Windows GUI installer. New work should use the Multi-OS path above.

---

## 3. Mobile / APK Track

Early mobile (Android) work is documented in:

**`Vespera_Mobile_Vision_Upgrade_Dossier.pdf`**

This covers the vision for an Android companion / operator client (APK). A dedicated `apk` branch is planned for the actual application code, build scripts and packaging once the multi-OS core is stable. The dossier remains the current reference for the mobile direction.

---

## Requirements (Multi-OS)

- Python 3.10+
- [Ollama](https://ollama.com) running locally (default `http://127.0.0.1:11434`)
- Packages in `multi_os/requirements.txt`
- Optional: NVIDIA drivers + `nvidia-ml-py`, Automatic1111 / ComfyUI, SearXNG, piper, faster-whisper, etc. for extended tools (see `multi_os/docs/TOOLS.md`)

---

## License

MIT

---

**Start here for new installs:**  
```bash
git clone https://github.com/vectisops/Vespera.git && cd Vespera && git checkout multi-os && cd multi_os
```
