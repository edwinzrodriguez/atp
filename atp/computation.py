"""
Computation module for ATP based on the Half-Latency Rule.

Definitions and assumptions (since the attached paper text isn't available here):
- Given arrays of IOPS (x) and latency (y), sorted by increasing IOPS,
  the "half-latency" threshold L_half can be defined by different rules:
  1) midrange: (min_latency + max_latency) / 2  [default]
  2) double_min: 2 * min_latency

- The knee is the smallest IOPS where latency crosses L_half. If no exact
  point matches, use linear interpolation between the nearest points
  surrounding L_half.

- ATP is defined as the IOPS at the knee.

The functions use numpy and accept/return numpy arrays.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Literal, Optional, Tuple


HalfRule = Literal["midrange", "double_min"]


@dataclass
class KneeResult:
    atp_iops: float
    knee_latency: float
    half_latency: float
    knee_index_left: Optional[int]
    knee_index_right: Optional[int]


def _validate_xy(iops: np.ndarray, latency: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    if iops.ndim != 1 or latency.ndim != 1:
        raise ValueError("iops and latency must be 1D arrays")
    if iops.size != latency.size:
        raise ValueError("iops and latency must be the same length")
    if iops.size < 2:
        raise ValueError("need at least two points to determine a knee")
    mask = ~(np.isnan(iops) | np.isnan(latency))
    iops = iops[mask]
    latency = latency[mask]
    if iops.size < 2:
        raise ValueError("not enough valid points after removing NaNs")
    # sort by iops ascending
    order = np.argsort(iops)
    return iops, latency
    # return iops[order], latency[order]


def moving_average(y: np.ndarray, window: int) -> np.ndarray:
    if window is None or window <= 1:
        return y
    window = int(window)
    if window > y.size:
        window = y.size
    # centered moving average with reflection padding
    pad = window // 2
    y_pad = np.pad(y, pad_width=pad, mode="edge")
    kernel = np.ones(window) / window
    y_smooth = np.convolve(y_pad, kernel, mode="valid")
    # adjust length to original size
    if y_smooth.size > y.size:
        start = (y_smooth.size - y.size) // 2
        y_smooth = y_smooth[start:start + y.size]
    return y_smooth


def compute_half_latency(latency: np.ndarray, rule: HalfRule = "midrange") -> float:
    lat_min = float(np.nanmin(latency))
    lat_max = float(np.nanmax(latency))
    if rule == "midrange":
        return 0.5 * (lat_min + lat_max)
    elif rule == "double_min":
        return 2.0 * lat_min
    else:
        raise ValueError(f"Unknown half-latency rule: {rule}")


def _interpolate_knee(iops: np.ndarray, latency: np.ndarray, L_half: float) -> Tuple[float, float, Optional[int], Optional[int]]:
    # find first index where latency >= L_half
    idx = np.argmax(latency >= L_half)
    if not (latency >= L_half).any():
        # never crosses, return last point
        return float(iops[-1]), float(latency[-1]), iops.size - 2 if iops.size >= 2 else None, iops.size - 1
    if latency[idx] == L_half or idx == 0:
        # if idx == 0, there is no left index; otherwise left is idx-1
        left = None if idx == 0 else idx - 1
        return float(iops[idx]), float(latency[idx]), left, idx
    # linear interpolation between (idx-1) and idx
    x0, y0 = float(iops[idx - 1]), float(latency[idx - 1])
    x1, y1 = float(iops[idx]), float(latency[idx])
    if y1 == y0:
        return x1, y1, idx - 1, idx
    t = (L_half - y0) / (y1 - y0)
    xk = x0 + t * (x1 - x0)
    return float(xk), float(L_half), idx - 1, idx


def find_knee_half_latency(
    iops: np.ndarray,
    latency: np.ndarray,
    rule: HalfRule = "midrange",
    smooth_window: Optional[int] = None,
) -> KneeResult:
    """
    Compute ATP using the Half-Latency knee rule.

    Parameters:
        iops: array-like of IOPS values.
        latency: array-like of corresponding latency values.
        rule: 'midrange' or 'double_min' (see module docstring).
        smooth_window: optional integer window for centered moving average on latency.

    Returns: KneeResult with ATP (IOPS at knee), knee latency, half-latency, indices.
    """
    x = np.asarray(iops, dtype=float)
    y = np.asarray(latency, dtype=float)
    x, y = _validate_xy(x, y)
    y_use = moving_average(y, smooth_window) if smooth_window and smooth_window > 1 else y
    L_half = compute_half_latency(y_use, rule=rule)
    atp_iops, knee_latency, il, ir = _interpolate_knee(x, y_use, L_half)
    return KneeResult(atp_iops=atp_iops, knee_latency=knee_latency, half_latency=L_half, knee_index_left=il, knee_index_right=ir)
