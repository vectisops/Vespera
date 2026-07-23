"""Configuration handling for Vespera multi-OS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from platformdirs import user_config_dir, user_data_dir

APP_NAME = "vespera"
APP_AUTHOR = "vectisops"

CONFIG_DIR = Path(user_config_dir(APP_NAME, APP_AUTHOR))
DATA_DIR = Path(user_data_dir(APP_NAME, APP_AUTHOR))
CONFIG_FILE = CONFIG_DIR / "operator.json"

DEFAULT_CONFIG: Dict[str, Any] = {
    "active_persona": "pure_logic",
    "default_model": "gemma3:12b",
    "ollama_host": "http://127.0.0.1:11434",
    "last_hardware_scan": None,
    "feature_packs": {
        "vision": False,
        "osint": False,
        "lab": False,
    },
}


def ensure_dirs() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> Dict[str, Any]:
    ensure_dirs()
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            cfg = DEFAULT_CONFIG.copy()
            cfg.update(data)
            return cfg
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(cfg: Dict[str, Any]) -> None:
    ensure_dirs()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def get_personas_dir() -> Path:
    package_personas = Path(__file__).parent / "personas"
    if package_personas.exists():
        return package_personas
    user_personas = DATA_DIR / "personas"
    user_personas.mkdir(parents=True, exist_ok=True)
    return user_personas


def list_personas() -> Dict[str, Path]:
    pdir = get_personas_dir()
    return {p.stem: p for p in pdir.glob("*.md")}


def load_persona(name: str) -> str:
    personas = list_personas()
    if name not in personas:
        raise FileNotFoundError(f"Persona '{name}' not found. Available: {list(personas)}")
    return personas[name].read_text(encoding="utf-8")
