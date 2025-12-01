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


def make_comparison_lines(
    res1: KneeResult,
    res2: KneeResult,
    label1: str = "A",
    label2: str = "B",
    latency_units: str = "ms",
) -> Sequence[str]:
    """
    Create human-readable lines comparing two KneeResult objects.
    Reports absolute and percentage differences for ATP (IOPS at knee)
    and knee latency.
    """
    # Differences for ATP (IOPS)
    atp1, atp2 = float(res1.atp_iops), float(res2.atp_iops)
    lat1, lat2 = float(res1.knee_latency), float(res2.knee_latency)

    def pct(a: float, b: float) -> float:
        if a == 0:
            return float('inf') if b != 0 else 0.0
        return 100.0 * (b - a) / abs(a)

    lines = []
    lines.append("Comparison Summary")
    lines.append("")
    lines.append(f"Dataset {label1}: ATP={atp1:.3f} IOPS, Knee Latency={lat1:.3f} {latency_units}, Half-Latency={res1.half_latency:.3f} {latency_units}")
    lines.append(f"Dataset {label2}: ATP={atp2:.3f} IOPS, Knee Latency={lat2:.3f} {latency_units}, Half-Latency={res2.half_latency:.3f} {latency_units}")
    lines.append("")
    d_atp = atp2 - atp1
    p_atp = pct(atp1, atp2)
    d_lat = lat2 - lat1
    p_lat = pct(lat1, lat2)
    lines.append(f"ATP difference ({label2} - {label1}): {d_atp:.3f} IOPS ({p_atp:.2f}%)")
    lines.append(f"Knee latency difference ({label2} - {label1}): {d_lat:.3f} {latency_units} ({p_lat:.2f}%)")
    return lines
