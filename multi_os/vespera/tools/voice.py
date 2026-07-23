"""Voice STT/TTS and a simple voice chat turn."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional

WHISPER_MODEL = os.environ.get("VESPERA_WHISPER_MODEL", "base.en")
PIPER_BIN = os.environ.get("VESPERA_PIPER_BIN", "piper")
PIPER_MODEL = os.environ.get("VESPERA_PIPER_MODEL", "")


def status() -> Dict[str, Any]:
    stt = "none"
    tts = "none"
    try:
        import faster_whisper  # noqa: F401
        stt = "faster-whisper"
    except Exception:
        if shutil.which("whisper-cli") or shutil.which("whisper"):
            stt = "whisper-cli"
    if shutil.which(PIPER_BIN):
        tts = "piper"
    elif shutil.which("tts"):
        tts = "coqui-tts"
    return {
        "ok": stt != "none" or tts != "none",
        "stt": stt,
        "tts": tts,
        "whisper_model": WHISPER_MODEL,
        "piper_model": PIPER_MODEL or "(set VESPERA_PIPER_MODEL)",
        "notes": "pip install faster-whisper; install piper for TTS.",
    }


def stt(audio_path: str, language: Optional[str] = "en") -> Dict[str, Any]:
    path = Path(audio_path)
    if not path.is_file():
        raise FileNotFoundError(audio_path)
    try:
        from faster_whisper import WhisperModel
        model = WhisperModel(WHISPER_MODEL, device="cuda", compute_type="float16")
        segments, info = model.transcribe(str(path), language=language)
        text = " ".join(s.text.strip() for s in segments).strip()
        return {"text": text, "language": info.language, "backend": "faster-whisper"}
    except Exception:
        pass
    cli = shutil.which("whisper-cli") or shutil.which("whisper")
    if not cli:
        raise RuntimeError("No STT backend. Install faster-whisper or whisper.cpp.")
    out = subprocess.run(
        [cli, "-m", WHISPER_MODEL, "-f", str(path), "-l", language or "en"],
        capture_output=True, text=True, timeout=600,
    )
    return {"text": out.stdout.strip(), "backend": "whisper-cli", "stderr": out.stderr[-500:]}


def tts(text: str, out_path: str = "outputs/voice/out.wav") -> Dict[str, Any]:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    if shutil.which(PIPER_BIN) and PIPER_MODEL:
        proc = subprocess.run(
            [PIPER_BIN, "--model", PIPER_MODEL, "--output_file", out_path],
            input=text, text=True, capture_output=True, timeout=120,
        )
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr)
        return {"path": str(Path(out_path).resolve()), "backend": "piper"}
    if shutil.which("tts"):
        subprocess.run(["tts", "--text", text, "--out_path", out_path], check=True, capture_output=True, timeout=180)
        return {"path": str(Path(out_path).resolve()), "backend": "coqui-tts"}
    raise RuntimeError("No TTS backend. Install piper (set VESPERA_PIPER_MODEL) or Coqui TTS.")


def chat_turn(
    audio_path: str,
    model: str = "gemma3:12b",
    system_prompt: str = "You are a helpful voice assistant. Keep replies concise.",
    ollama_host: str = "http://127.0.0.1:11434",
) -> Dict[str, Any]:
    from ..ollama_client import OllamaClient
    transcribed = stt(audio_path)
    user_text = transcribed.get("text") or ""
    client = OllamaClient(ollama_host)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text},
    ]
    resp = client.chat(model=model, messages=messages, stream=False)
    if isinstance(resp, dict):
        reply = resp.get("message", {}).get("content") or resp.get("response") or str(resp)
    else:
        reply = str(resp)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        audio_out = tmp.name
    spoken = tts(reply, out_path=audio_out)
    return {
        "user_text": user_text,
        "reply_text": reply,
        "audio_path": spoken["path"],
        "stt_backend": transcribed.get("backend"),
        "tts_backend": spoken.get("backend"),
    }
