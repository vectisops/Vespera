"""
Cross-platform hardware telemetry and compatibility matrix for Vespera.

Works on Linux, macOS, and Windows.
Uses psutil for RAM/CPU, optional nvidia-ml-py / nvidia-smi for NVIDIA VRAM,
and graceful fallbacks.

Includes optional hardware profiles (e.g. MSI Raider GE78 HX 14VIG with RTX 4090 Laptop)
that can tighten recommendations when the machine matches known signatures.
"""

from __future__ import annotations

import platform
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import psutil

try:
    from pynvml import (
        nvmlInit,
        nvmlShutdown,
        nvmlDeviceGetCount,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetName,
        nvmlDeviceGetMemoryInfo,
    )
    HAS_NVML = True
except Exception:
    HAS_NVML = False


@dataclass
class GPUInfo:
    name: str = "Unknown"
    total_vram_mb: float = 0.0
    free_vram_mb: float = 0.0
    used_vram_mb: float = 0.0
    index: int = 0
    vendor: str = "unknown"


@dataclass
class HardwareReport:
    os_name: str
    os_release: str
    architecture: str
    cpu_count_logical: int
    cpu_count_physical: int
    cpu_freq_mhz: Optional[float]
    total_ram_gb: float
    available_ram_gb: float
    used_ram_percent: float
    gpus: List[GPUInfo] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    profile_name: Optional[str] = None
    profile_overrides: Dict[str, Any] = field(default_factory=dict)

    def recommended_quant_for_params(self, params_billion: float = 12.0) -> Dict[str, Any]:
        """
        Conservative quantisation advice.
        Prefer profile overrides when a known machine is detected.
        """
        if self.profile_overrides and "quant_12b" in self.profile_overrides:
            return self.profile_overrides["quant_12b"]

        free_vram = max((g.free_vram_mb for g in self.gpus), default=0.0)
        free_ram_mb = self.available_ram_gb * 1024

        estimates = {
            "Q2_K": 4.5,
            "Q3_K_M": 5.8,
            "Q4_K_M": 7.2,
            "Q5_K_M": 8.5,
            "Q6_K": 10.0,
            "Q8_0": 13.0,
            "FP16": 24.0,
        }

        budget_gb = (free_vram / 1024.0) if free_vram > 2048 else (free_ram_mb / 1024.0 * 0.55)

        safe = [q for q, size in estimates.items() if size <= budget_gb * 0.85]

        return {
            "budget_gb": round(budget_gb, 2),
            "safe_quants": safe[::-1] if safe else ["Q2_K (very tight)"],
            "recommended": safe[-1] if safe else "Q2_K",
            "note": "Conservative estimate. Always monitor actual OOM / context length.",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "os": f"{self.os_name} {self.os_release}",
            "arch": self.architecture,
            "cpu": {
                "logical": self.cpu_count_logical,
                "physical": self.cpu_count_physical,
                "freq_mhz": self.cpu_freq_mhz,
            },
            "ram_gb": {
                "total": round(self.total_ram_gb, 2),
                "available": round(self.available_ram_gb, 2),
                "used_percent": round(self.used_ram_percent, 1),
            },
            "gpus": [
                {
                    "name": g.name,
                    "vendor": g.vendor,
                    "total_vram_mb": round(g.total_vram_mb, 1),
                    "free_vram_mb": round(g.free_vram_mb, 1),
                }
                for g in self.gpus
            ],
            "notes": self.notes,
            "profile": self.profile_name,
            "recommendation_12b": self.recommended_quant_for_params(12.0),
        }


def _match_raider_ge78(report: HardwareReport) -> bool:
    """Heuristic match for MSI Raider GE78 HX class machines."""
    if report.total_ram_gb < 48:
        return False
    for g in report.gpus:
        name = g.name.lower()
        if "4090" in name and ("laptop" in name or g.total_vram_mb < 20000):
            return True
    return False


def apply_profile(report: HardwareReport) -> HardwareReport:
    """Attach a known profile and tighten recommendations if matched."""
    if _match_raider_ge78(report):
        report.profile_name = "MSI Raider GE78 HX (RTX 4090 Laptop class)"
        report.profile_overrides = {
            "quant_12b": {
                "budget_gb": 14.5,
                "safe_quants": ["Q4_K_M", "Q5_K_M", "Q6_K", "Q8_0"],
                "recommended": "Q5_K_M",
                "concurrent_12b": 1,
                "note": (
                    "RTX 4090 Laptop (16 GB). Q5_K_M is the sweet spot for Gemma-3-12B "
                    "with healthy context. Q6_K / Q8_0 viable for shorter contexts. "
                    "Avoid simultaneous large models unless using aggressive offload."
                ),
            },
            "thermal_note": "Laptop form factor – sustained high load will thermal-throttle. Prefer shorter generations or lower quant under long sessions.",
            "storage_note": "Dual NVMe configuration typical – keep models on the faster drive.",
        }
        report.notes.append(
            "Matched known high-end mobile workstation profile (Raider GE78 / 4090 Laptop class). "
            "Using tightened quantisation matrix."
        )
        if "thermal_note" in report.profile_overrides:
            report.notes.append(report.profile_overrides["thermal_note"])
    return report


def _get_nvidia_gpus() -> List[GPUInfo]:
    gpus: List[GPUInfo] = []
    if not HAS_NVML:
        return gpus
    try:
        nvmlInit()
        count = nvmlDeviceGetCount()
        for i in range(count):
            handle = nvmlDeviceGetHandleByIndex(i)
            name = nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode("utf-8", errors="ignore")
            mem = nvmlDeviceGetMemoryInfo(handle)
            gpus.append(
                GPUInfo(
                    name=str(name),
                    total_vram_mb=mem.total / (1024 * 1024),
                    free_vram_mb=mem.free / (1024 * 1024),
                    used_vram_mb=mem.used / (1024 * 1024),
                    index=i,
                    vendor="nvidia",
                )
            )
        nvmlShutdown()
    except Exception:
        pass
    return gpus


def _try_nvidia_smi() -> List[GPUInfo]:
    gpus = []
    if not shutil.which("nvidia-smi"):
        return gpus
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=5,
        )
        for i, line in enumerate(out.strip().splitlines()):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 3:
                gpus.append(
                    GPUInfo(
                        name=parts[0],
                        total_vram_mb=float(parts[1]),
                        free_vram_mb=float(parts[2]),
                        used_vram_mb=float(parts[1]) - float(parts[2]),
                        index=i,
                        vendor="nvidia",
                    )
                )
    except Exception:
        pass
    return gpus


def scan_hardware(apply_profiles: bool = True) -> HardwareReport:
    mem = psutil.virtual_memory()
    freq = psutil.cpu_freq()

    report = HardwareReport(
        os_name=platform.system(),
        os_release=platform.release(),
        architecture=platform.machine(),
        cpu_count_logical=psutil.cpu_count(logical=True) or 0,
        cpu_count_physical=psutil.cpu_count(logical=False) or 0,
        cpu_freq_mhz=freq.current if freq else None,
        total_ram_gb=mem.total / (1024**3),
        available_ram_gb=mem.available / (1024**3),
        used_ram_percent=mem.percent,
    )

    gpus = _get_nvidia_gpus()
    if not gpus:
        gpus = _try_nvidia_smi()
    report.gpus = gpus

    if not gpus:
        report.notes.append(
            "No NVIDIA GPU detected (or drivers/NVML missing). "
            "Falling back to system RAM for model sizing. "
            "Apple Silicon / AMD users: VRAM detection is limited in this version."
        )

    if report.os_name == "Linux":
        report.notes.append("Linux detected – optimal path for sovereign / offline operation.")
    elif report.os_name == "Darwin":
        report.notes.append("macOS detected – Metal acceleration available via Ollama if configured.")
    elif report.os_name == "Windows":
        report.notes.append(
            "Windows detected – native Python path active. "
            "WSL2 remains optional for advanced toolkits."
        )

    if apply_profiles:
        report = apply_profile(report)

    return report


def print_report(report: Optional[HardwareReport] = None) -> None:
    if report is None:
        report = scan_hardware()

    try:
        from rich.console import Console
        from rich.table import Table
        from rich.panel import Panel

        console = Console()
        title = "Vespera Hardware Prescan"
        if report.profile_name:
            title += f"  [{report.profile_name}]"
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("Metric", style="dim")
        table.add_column("Value")

        table.add_row("OS", f"{report.os_name} {report.os_release} ({report.architecture})")
        table.add_row("CPU", f"{report.cpu_count_physical}c / {report.cpu_count_logical}t")
        table.add_row(
            "System RAM",
            f"{report.total_ram_gb:.1f} GB total  |  {report.available_ram_gb:.1f} GB free  ({report.used_ram_percent:.0f}% used)",
        )

        if report.gpus:
            for g in report.gpus:
                table.add_row(
                    f"GPU [{g.index}]",
                    f"{g.name}  |  {g.total_vram_mb/1024:.1f} GB total  |  {g.free_vram_mb/1024:.1f} GB free",
                )
        else:
            table.add_row("GPU", "None detected / not NVIDIA")

        rec = report.recommended_quant_for_params(12.0)
        table.add_row(
            "12B model advice",
            f"Budget ~{rec['budget_gb']} GB  →  recommended: {rec['recommended']}",
        )
        if "concurrent_12b" in rec:
            table.add_row("Concurrent 12B", str(rec["concurrent_12b"]))

        console.print(table)
        if report.notes:
            console.print(Panel("\n".join(f"• {n}" for n in report.notes), title="Notes", border_style="yellow"))
    except ImportError:
        d = report.to_dict()
        print("=== Vespera Hardware Prescan ===")
        for k, v in d.items():
            print(f"{k}: {v}")


if __name__ == "__main__":
    print_report()
