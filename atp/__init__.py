"""
ATP (Application Turning Point) analysis tools.

This package provides utilities to compute the knee of a latency-vs-IOPS
curve based on the Half-Latency Rule, along with input/output helpers and
plot generation.

High-level entry points:
- atp.computation.find_knee_half_latency
- atp.io.read_table
- atp.output.write_text_report
- atp.plotting.plot_latency_curve

CLI usage: python -m atp.cli --help
"""

from .computation import find_knee_half_latency, compute_half_latency

__all__ = [
    "find_knee_half_latency",
    "compute_half_latency",
]
