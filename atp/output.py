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


def write_comparison_report(
    res1: KneeResult,
    res2: KneeResult,
    path1: str,
    path2: str,
    label1: str = "A",
    label2: str = "B",
    latency_units: str = "ms",
    out_path: Optional[str] = None,
) -> None:
    """
    Write a standalone comparison report showing all ATP metrics with absolute
    and percentage differences between two KneeResult objects.
    """
    def pct(a: float, b: float) -> str:
        if a == 0:
            return "N/A" if b != 0 else "0.00%"
        return f"{100.0 * (b - a) / abs(a):+.2f}%"

    def sign(v: float) -> str:
        return f"{v:+.3f}"

    metrics = [
        ("Half-Latency", res1.half_latency, res2.half_latency, latency_units),
        ("Knee Latency", res1.knee_latency, res2.knee_latency, latency_units),
        ("ATP (IOPS)",   res1.atp_iops,     res2.atp_iops,     "IOPS"),
    ]

    col_metric = 20
    col_val    = 14

    header = (
        f"{'Metric':<{col_metric}}"
        f"{label1:>{col_val}}"
        f"{label2:>{col_val}}"
        f"{'Abs Diff':>{col_val}}"
        f"{'% Diff':>{col_val}}"
    )
    sep = "-" * len(header)

    rows = []
    for name, v1, v2, unit in metrics:
        label = f"{name} ({unit})"
        rows.append(
            f"{label:<{col_metric}}"
            f"{v1:>{col_val}.3f}"
            f"{v2:>{col_val}.3f}"
            f"{sign(v2 - v1):>{col_val}}"
            f"{pct(v1, v2):>{col_val}}"
        )

    lines = [
        "ATP Comparison Report",
        "=" * len(header),
        f"{label1}: {path1}",
        f"{label2}: {path2}",
        "",
        header,
        sep,
        *rows,
        sep,
    ]
    text = "\n".join(lines) + "\n"

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)
