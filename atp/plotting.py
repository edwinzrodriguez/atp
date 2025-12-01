"""
Plotting utilities for ATP analysis.
"""

from __future__ import annotations

from typing import Optional

import numpy as np

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None  # type: ignore

from .computation import KneeResult


def _require_matplotlib():
    if plt is None:
        raise RuntimeError("matplotlib is required for plotting. Please install matplotlib.")


def plot_latency_curve(
    iops: np.ndarray,
    latency: np.ndarray,
    result: KneeResult,
    title: Optional[str] = None,
    latency_units: str = "ms",
    save_pdf: Optional[str] = None,
    show: bool = False,
):
    """
    Plot latency vs IOPS, half-latency horizontal line, and knee point.
    If save_pdf is provided, writes a PDF; if show=True, displays a window.
    Both can be used together.
    """
    _require_matplotlib()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot(iops, latency, marker="o", linestyle="-", color="#1f77b4", label="Latency")
    ax.axhline(result.half_latency, color="#d62728", linestyle="--", label="Half-latency")
    ax.plot([result.atp_iops], [result.knee_latency], marker="x", color="#2ca02c", markersize=10, label="Knee (ATP)")
    ax.set_xlabel("IOPS")
    ax.set_ylabel(f"Latency ({latency_units})")
    ax.grid(True, linestyle=":", alpha=0.5)
    if title:
        ax.set_title(title)
    ax.legend()

    if save_pdf:
        fig.savefig(save_pdf, format="pdf", bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_latency_curve_compare(
    iops1: np.ndarray,
    latency1: np.ndarray,
    res1: KneeResult,
    iops2: np.ndarray,
    latency2: np.ndarray,
    res2: KneeResult,
    label1: str = "A",
    label2: str = "B",
    title: Optional[str] = None,
    latency_units: str = "ms",
    save_pdf: Optional[str] = None,
    show: bool = False,
):
    """
    Plot two latency vs IOPS curves with their half-latency lines and knee points.
    """
    _require_matplotlib()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(iops1, latency1, marker="o", linestyle="-", color="#1f77b4", label=f"Latency {label1}")
    ax.plot(iops2, latency2, marker="s", linestyle="-", color="#ff7f0e", label=f"Latency {label2}")
    ax.axhline(res1.half_latency, color="#d62728", linestyle="--", alpha=0.8, label=f"Half-latency {label1}")
    ax.axhline(res2.half_latency, color="#9467bd", linestyle=":", alpha=0.8, label=f"Half-latency {label2}")
    ax.plot([res1.atp_iops], [res1.knee_latency], marker="x", color="#2ca02c", markersize=10, label=f"Knee {label1}")
    ax.plot([res2.atp_iops], [res2.knee_latency], marker="x", color="#17becf", markersize=10, label=f"Knee {label2}")
    ax.set_xlabel("IOPS")
    ax.set_ylabel(f"Latency ({latency_units})")
    ax.grid(True, linestyle=":", alpha=0.5)
    if title:
        ax.set_title(title)
    ax.legend(ncol=2)

    if save_pdf:
        fig.savefig(save_pdf, format="pdf", bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)
