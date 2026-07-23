"""Configuration handling for Vespera multi-OS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

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
    """Return the personas directory (package first, then user data)."""
    package_personas = Path(__file__).parent / "personas"
    if package_personas.exists():
        return package_personas
    user_personas = DATA_DIR / "personas"
    user_personas.mkdir(parents=True, exist_ok=True)
    return user_personas


def _persona_key(path: Path, root: Path) -> str:
    """
    Build a stable persona name from a file path.

    Prefer the plain stem when unique. If the file lives in a recognised
    category folder (deep / task / explicit), we still use the stem so
    existing commands (`--persona intimate_partner`) keep working.
    """
    return path.stem


def list_personas() -> Dict[str, Path]:
    """
    Discover all persona .md files, including those in sub-folders
    (deep/, task/, explicit/, etc.).

    Returns a dict of {persona_name: path}.
    If two files share the same stem, the one closer to the root wins
    and the deeper one is stored under a namespaced key (category/stem).
    """
    pdir = get_personas_dir()
    found: Dict[str, Path] = {}
    collisions: Dict[str, Path] = {}

    # Recursive search for every .md file under personas/
    for path in sorted(pdir.rglob("*.md")):
        if not path.is_file():
            continue
        # Skip README files
        if path.stem.lower() in {"readme", "license", "changelog"}:
            continue

        key = _persona_key(path, pdir)
        if key in found:
            # Collision – keep the first (shallower) and namespace the new one
            try:
                rel = path.relative_to(pdir)
                category = rel.parts[0] if len(rel.parts) > 1 else "extra"
            except ValueError:
                category = "extra"
            namespaced = f"{category}/{path.stem}"
            collisions[namespaced] = path
        else:
            found[key] = path

    found.update(collisions)
    return found


def list_personas_grouped() -> Dict[str, Dict[str, Path]]:
    """
    Same discovery as list_personas(), but grouped by top-level category.

    Categories are the immediate sub-folder names (deep, task, explicit)
    or "_root" for files sitting directly in personas/.
    """
    pdir = get_personas_dir()
    grouped: Dict[str, Dict[str, Path]] = {}

    for path in sorted(pdir.rglob("*.md")):
        if not path.is_file():
            continue
        if path.stem.lower() in {"readme", "license", "changelog"}:
            continue

        try:
            rel = path.relative_to(pdir)
        except ValueError:
            continue

        if len(rel.parts) == 1:
            category = "_root"
        else:
            category = rel.parts[0]

        grouped.setdefault(category, {})[path.stem] = path

    return grouped


def load_persona(name: str) -> str:
    """
    Load a persona by name.

    Accepts either a plain stem ("intimate_partner") or a namespaced
    form ("explicit/intimate_partner") in case of collisions.
    """
    personas = list_personas()

    # Direct hit
    if name in personas:
        return personas[name].read_text(encoding="utf-8")

    # Try stripping a category prefix if the user passed one
    if "/" in name:
        bare = name.split("/", 1)[-1]
        if bare in personas:
            return personas[bare].read_text(encoding="utf-8")

    raise FileNotFoundError(
        f"Persona '{name}' not found. Available: {sorted(personas.keys())}"
    )
