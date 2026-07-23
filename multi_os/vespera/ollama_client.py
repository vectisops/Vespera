"""Thin wrapper around the Ollama Python client / HTTP API."""

from __future__ import annotations

from typing import Any, Dict, Generator, List, Optional

try:
    import ollama
    HAS_OLLAMA_PKG = True
except ImportError:
    HAS_OLLAMA_PKG = False

import httpx


class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434"):
        self.host = host.rstrip("/")
        self._client = None
        if HAS_OLLAMA_PKG:
            self._client = ollama.Client(host=self.host)

    def is_available(self) -> bool:
        try:
            r = httpx.get(f"{self.host}/api/tags", timeout=3.0)
            return r.status_code == 200
        except Exception:
            return False

    def list_models(self) -> List[Dict[str, Any]]:
        if self._client:
            return self._client.list().get("models", [])
        r = httpx.get(f"{self.host}/api/tags", timeout=10.0)
        r.raise_for_status()
        return r.json().get("models", [])

    def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs,
    ) -> Any:
        if self._client:
            return self._client.chat(model=model, messages=messages, stream=stream, **kwargs)
        # Fallback raw HTTP
        payload = {"model": model, "messages": messages, "stream": stream, **kwargs}
        if stream:
            def gen():
                with httpx.stream("POST", f"{self.host}/api/chat", json=payload, timeout=None) as resp:
                    for line in resp.iter_lines():
                        if line:
                            yield line
            return gen()
        r = httpx.post(f"{self.host}/api/chat", json=payload, timeout=120.0)
        r.raise_for_status()
        return r.json()

    def pull(self, model: str) -> Generator[Dict[str, Any], None, None]:
        """Pull a model with progress (best-effort)."""
        if self._client:
            for progress in self._client.pull(model, stream=True):
                yield progress
            return
        # Simple non-streaming fallback
        r = httpx.post(f"{self.host}/api/pull", json={"name": model}, timeout=None)
        r.raise_for_status()
        yield {"status": "done"}
