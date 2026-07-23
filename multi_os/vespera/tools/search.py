"""Web search – SearXNG preferred; DuckDuckGo HTML fallback."""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List
from urllib.error import URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen

SEARX = os.environ.get("VESPERA_SEARXNG_URL", "http://127.0.0.1:8080")


def status() -> Dict[str, Any]:
    ok = False
    detail = "searxng unreachable; DDG fallback available"
    try:
        with urlopen(SEARX.rstrip("/") + "/healthz", timeout=2) as r:
            ok = r.status == 200
            detail = "searxng ok"
    except Exception:
        try:
            with urlopen(SEARX.rstrip("/") + "/", timeout=2) as r:
                ok = True
                detail = "searxng root ok"
        except Exception as e:
            detail = f"searxng down ({e}); will use DDG HTML"
    return {"ok": True, "searxng": ok, "url": SEARX, "detail": detail}


def web_search(query: str, limit: int = 8) -> Dict[str, Any]:
    results = _searxng(query, limit)
    if results is not None:
        return {"engine": "searxng", "query": query, "results": results}
    return {"engine": "duckduckgo_html", "query": query, "results": _ddg(query, limit)}


def _searxng(query: str, limit: int) -> List[Dict[str, str]] | None:
    try:
        qs = urlencode({"q": query, "format": "json"})
        req = Request(SEARX.rstrip("/") + "/search?" + qs, headers={"User-Agent": "Vespera/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        out = []
        for item in (data.get("results") or [])[:limit]:
            out.append({
                "title": item.get("title") or "",
                "url": item.get("url") or "",
                "snippet": item.get("content") or item.get("snippet") or "",
            })
        return out
    except Exception:
        return None


def _ddg(query: str, limit: int) -> List[Dict[str, str]]:
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 Vespera/1.0"})
    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        raise RuntimeError(f"Search failed: {e}") from e
    pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'class="result__snippet"[^>]*>(.*?)</',
        re.I | re.S,
    )
    out: List[Dict[str, str]] = []
    for m in pattern.finditer(html):
        title = re.sub("<.*?>", "", m.group(2)).strip()
        snippet = re.sub("<.*?>", "", m.group(3)).strip()
        out.append({"title": title, "url": m.group(1), "snippet": snippet})
        if len(out) >= limit:
            break
    return out
