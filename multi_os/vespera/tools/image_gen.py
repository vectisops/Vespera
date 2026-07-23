"""Image generation via local Stable Diffusion frontends.

Env:
  VESPERA_SD_URL=http://127.0.0.1:7861
  VESPERA_SD_BACKEND=a1111|comfy
"""

from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_URL = os.environ.get("VESPERA_SD_URL", "http://127.0.0.1:7861")
BACKEND = os.environ.get("VESPERA_SD_BACKEND", "a1111")


def status() -> Dict[str, Any]:
    base = DEFAULT_URL.rstrip("/")
    ok = False
    detail = "unreachable"
    try:
        if BACKEND == "a1111":
            with urlopen(base + "/sdapi/v1/sd-models", timeout=2) as r:
                ok = r.status == 200
                detail = "a1111 ok"
        else:
            with urlopen(base + "/system_stats", timeout=2) as r:
                ok = r.status == 200
                detail = "comfy ok"
    except Exception as e:
        detail = str(e)
    return {
        "ok": ok,
        "backend": BACKEND,
        "url": base,
        "detail": detail,
        "notes": "Install Automatic1111 or ComfyUI locally; point VESPERA_SD_URL at it.",
    }


def generate(
    prompt: str,
    negative_prompt: str = "",
    steps: int = 25,
    width: int = 768,
    height: int = 768,
    cfg_scale: float = 7.0,
    seed: int = -1,
    out_dir: str = "outputs/images",
) -> Dict[str, Any]:
    if BACKEND == "comfy":
        raise RuntimeError(
            "ComfyUI path is a stub here. Set VESPERA_SD_BACKEND=a1111 or extend with your workflow."
        )
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "steps": steps,
        "width": width,
        "height": height,
        "cfg_scale": cfg_scale,
        "seed": seed,
    }
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        DEFAULT_URL.rstrip("/") + "/sdapi/v1/txt2img",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=300) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        raise RuntimeError(
            f"SD backend unreachable at {DEFAULT_URL}. Start A1111 with --api. ({e})"
        ) from e

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, b64 in enumerate(body.get("images") or []):
        raw = base64.b64decode(b64.split(",", 1)[-1])
        p = out / f"vespera_{i}.png"
        p.write_bytes(raw)
        paths.append(str(p.resolve()))
    return {"paths": paths, "info": body.get("info"), "backend": "a1111"}
