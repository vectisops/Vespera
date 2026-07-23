"""Network diagnostics and light forensics – defensive / authorized use only."""

from __future__ import annotations

import shutil
import socket
import subprocess
from pathlib import Path
from typing import Any, Dict, List


def status() -> Dict[str, Any]:
    bins = {
        "ping": bool(shutil.which("ping")),
        "dig": bool(shutil.which("dig")),
        "nslookup": bool(shutil.which("nslookup")),
        "ss": bool(shutil.which("ss")),
        "ip": bool(shutil.which("ip")),
        "traceroute": bool(shutil.which("traceroute") or shutil.which("tracepath")),
        "curl": bool(shutil.which("curl")),
    }
    return {
        "ok": any(bins.values()),
        "binaries": bins,
        "notes": "Defensive diagnostics only. Own/authorized networks.",
    }


def _run(cmd: List[str], timeout: int = 20) -> Dict[str, Any]:
    if not shutil.which(cmd[0]):
        return {"cmd": cmd, "ok": False, "error": f"{cmd[0]} not found"}
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "cmd": cmd,
            "ok": p.returncode == 0,
            "stdout": p.stdout[-4000:],
            "stderr": p.stderr[-1000:],
            "code": p.returncode,
        }
    except Exception as e:
        return {"cmd": cmd, "ok": False, "error": str(e)}


def diagnose(host: str = "1.1.1.1", dns_name: str = "example.com") -> Dict[str, Any]:
    results: Dict[str, Any] = {"target_host": host, "dns_name": dns_name}
    results["ping"] = _run(["ping", "-c", "4", "-W", "2", host])
    if shutil.which("dig"):
        results["dns"] = _run(["dig", "+short", dns_name])
    elif shutil.which("nslookup"):
        results["dns"] = _run(["nslookup", dns_name])
    else:
        try:
            results["dns"] = {"ok": True, "stdout": socket.gethostbyname(dns_name)}
        except Exception as e:
            results["dns"] = {"ok": False, "error": str(e)}
    if shutil.which("ip"):
        results["routes"] = _run(["ip", "route"])
        results["addrs"] = _run(["ip", "-br", "addr"])
    if shutil.which("traceroute"):
        results["trace"] = _run(["traceroute", "-m", "12", host], timeout=45)
    elif shutil.which("tracepath"):
        results["trace"] = _run(["tracepath", "-m", "12", host], timeout=45)
    probes = {}
    for port in (11434, 8765, 7860, 22, 80, 443):
        probes[port] = _tcp_probe(host if host != "1.1.1.1" else "127.0.0.1", port)
    results["local_ports"] = probes
    return results


def forensics_light() -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if shutil.which("ss"):
        out["listening"] = _run(["ss", "-tulpn"])
        out["established"] = _run(["ss", "-tpn", "state", "established"])
    elif shutil.which("netstat"):
        out["listening"] = _run(["netstat", "-tulpn"])
    if Path("/etc/resolv.conf").exists():
        try:
            out["resolv_conf"] = Path("/etc/resolv.conf").read_text()
        except Exception as e:
            out["resolv_conf"] = str(e)
    if shutil.which("ip"):
        out["neighbours"] = _run(["ip", "neigh"])
    out["warning"] = "Authorized use only. Local passive snapshot, not remote exploitation."
    return out


def _tcp_probe(host: str, port: int, timeout: float = 0.6) -> Dict[str, Any]:
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return {"open": True}
    except Exception as e:
        return {"open": False, "error": str(e)}
