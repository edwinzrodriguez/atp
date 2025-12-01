"""
Input utilities for reading latency/IOPS data from CSV or XLSX.

Uses pandas for flexible parsing. Returns numpy arrays for computation.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple, Union

import numpy as np

try:
    import pandas as pd
except Exception as e:  # pragma: no cover - import-time dependency notice
    pd = None  # type: ignore


def _require_pandas():
    if pd is None:
        raise RuntimeError(
            "pandas is required for reading CSV/XLSX. Please install pandas (and openpyxl for .xlsx)."
        )


def read_table(
    path: str,
    iops_col: Union[str, int],
    latency_col: Union[str, int],
    sheet: Optional[Union[str, int]] = None,
    delimiter: Optional[str] = None,
    header: Optional[Union[int, None]] = 0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Read a CSV or XLSX file and extract IOPS and latency columns.

    Returns: (iops_np, latency_np, half_latency_dummy)
    The third array is a placeholder (zeros) to simplify downstream tabular reporting
    where a constant half-latency line may be displayed per row.
    """
    _require_pandas()
    ext = os.path.splitext(path)[1].lower()
    if ext in (".csv", ".tsv", ".txt"):
        df = pd.read_csv(path, delimiter=delimiter, header=header)
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet, header=header)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    # Allow integer index or column name
    if isinstance(iops_col, int):
        iops_series = df.iloc[:, iops_col]
    else:
        iops_series = df[iops_col]
    if isinstance(latency_col, int):
        lat_series = df.iloc[:, latency_col]
    else:
        lat_series = df[latency_col]

    iops = np.asarray(iops_series.to_numpy(dtype=float))
    latency = np.asarray(lat_series.to_numpy(dtype=float))
    half_dummy = np.zeros_like(latency)
    return iops, latency, half_dummy
