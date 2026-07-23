"""Central tool registry and status probes."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

from . import image_gen, video_gen, voice, search, netdiag

ToolFn = Callable[..., Any]

REGISTRY: Dict[str, Dict[str, Any]] = {
    "image.generate": {
        "pack": "media",
        "desc": "Generate an image via Automatic1111 / ComfyUI / SD WebUI API",
        "fn": image_gen.generate,
        "status": image_gen.status,
    },
    "video.generate": {
        "pack": "media",
        "desc": "Queue a short video generation job (ComfyUI / local pipeline)",
        "fn": video_gen.generate,
        "status": video_gen.status,
    },
    "voice.stt": {
        "pack": "voice",
        "desc": "Speech-to-text (faster-whisper / whisper.cpp)",
        "fn": voice.stt,
        "status": voice.status,
    },
    "voice.tts": {
        "pack": "voice",
        "desc": "Text-to-speech (piper / coqui)",
        "fn": voice.tts,
        "status": voice.status,
    },
    "voice.chat_turn": {
        "pack": "voice",
        "desc": "One voice turn: STT → LLM → TTS (needs Ollama + voice backends)",
        "fn": voice.chat_turn,
        "status": voice.status,
    },
    "search.web": {
        "pack": "search",
        "desc": "Web search via local SearXNG or DuckDuckGo HTML fallback",
        "fn": search.web_search,
        "status": search.status,
    },
    "net.diag": {
        "pack": "net",
        "desc": "Host diagnostics: ping, DNS, ports, routes (own network)",
        "fn": netdiag.diagnose,
        "status": netdiag.status,
    },
    "net.forensics_light": {
        "pack": "net",
        "desc": "Light passive forensics: connections, listeners, DNS cache hints",
        "fn": netdiag.forensics_light,
        "status": netdiag.status,
    },
}


def list_tools() -> List[Dict[str, str]]:
    return [
        {"name": k, "pack": v["pack"], "desc": v["desc"]}
        for k, v in sorted(REGISTRY.items())
    ]


def tool_status() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    seen_packs = set()
    for name, meta in REGISTRY.items():
        pack = meta["pack"]
        if pack in seen_packs:
            continue
        seen_packs.add(pack)
        try:
            out[pack] = meta["status"]()
        except Exception as e:
            out[pack] = {"ok": False, "error": str(e)}
    return out


def run_tool(name: str, **kwargs: Any) -> Any:
    if name not in REGISTRY:
        raise KeyError(f"Unknown tool '{name}'. Available: {list(REGISTRY)}")
    return REGISTRY[name]["fn"](**kwargs)
