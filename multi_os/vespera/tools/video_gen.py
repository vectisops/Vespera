"""Video generation hooks via ComfyUI workflow queue.

Env:
  VESPERA_VIDEO_URL=http://127.0.0.1:8188
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.error import URLError
from urllib.request import Request, urlopen

DEFAULT_URL = os.environ.get("VESPERA_VIDEO_URL", "http://127.0.0.1:8188")


def status() -> Dict[str, Any]:
    base = DEFAULT_URL.rstrip("/")
    ok = False
    detail = "unreachable"
    try:
        with urlopen(base + "/system_stats", timeout=2) as r:
            ok = r.status == 200
            detail = "comfy-like endpoint ok"
    except Exception as e:
        detail = str(e)
    return {
        "ok": ok,
        "url": base,
        "detail": detail,
        "notes": "ComfyUI + AnimateDiff / SVD / HunyuanVideo. Pass workflow_path= API JSON.",
    }


def generate(
    prompt: str = "",
    workflow_path: Optional[str] = None,
    frames: int = 24,
    out_dir: str = "outputs/video",
) -> Dict[str, Any]:
    if not workflow_path:
        return {
            "queued": False,
            "error": "Provide workflow_path= to a ComfyUI API-format workflow JSON.",
        }
    path = Path(workflow_path)
    if not path.is_file():
        raise FileNotFoundError(workflow_path)
    workflow = json.loads(path.read_text(encoding="utf-8"))
    payload = {"prompt": workflow}
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        DEFAULT_URL.rstrip("/") + "/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except URLError as e:
        raise RuntimeError(f"Video backend unreachable at {DEFAULT_URL}: {e}") from e
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    return {"queued": True, "response": body, "out_dir": out_dir, "frames_requested": frames}
