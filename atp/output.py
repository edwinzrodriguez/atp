"""
Output utilities: produce a text summary/report of the analysis.
"""

from __future__ import annotations

from typing import Optional, Sequence

import numpy as np

from .computation import KneeResult


def _fmt_float(x: float, nd: int = 3) -> str:
    return f"{x:.{nd}f}"


def write_text_report(
    iops: np.ndarray,
    latency: np.ndarray,
    result: KneeResult,
    out_path: Optional[str] = None,
    extra_lines: Optional[Sequence[str]] = None,
    latency_units: str = "ms",
):
    """
    Write a simple human-readable report.
    If out_path is None, print to stdout; otherwise, write to file.
    """
    lines = []
    lines.append("ATP Analysis Report (Half-Latency Rule)")
    lines.append("")
    lines.append(f"Points: {iops.size}")
    lines.append(f"Half-latency: {_fmt_float(result.half_latency)} {latency_units}")
    lines.append(f"Knee latency: {_fmt_float(result.knee_latency)} {latency_units}")
    lines.append(f"ATP (IOPS at knee): {_fmt_float(result.atp_iops)}")
    lines.append("")
    lines.append("Data (iops, latency, half-latency)")
    for x, y in zip(iops, latency):
        lines.append(f"{_fmt_float(float(x), 3)}, {_fmt_float(float(y), 3)}, {_fmt_float(result.half_latency, 3)}")
    if extra_lines:
        lines.append("")
        lines.extend(extra_lines)

    text = "\n".join(lines) + "\n"
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
