"""
Input utilities for reading latency/IOPS data from CSV or XLSX.

Uses pandas for flexible parsing. Returns numpy arrays for computation.
"""

from __future__ import annotations

import os
from typing import Optional, Tuple, Union
import xml.etree.ElementTree as ET

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


def read_xml_all_metrics(path: str) -> pd.DataFrame:
    """
    Read an XML summary file and return a pandas DataFrame with all metrics.
    """
    _require_pandas()
    tree = ET.parse(path)
    root = tree.getroot()
    
    data = []
    for run in root.findall("run"):
        row = {}
        # Basic run attributes
        for attr in ["time", "fingerprint", "version"]:
            if run.get(attr):
                row[attr] = run.get(attr)
        
        # business_metric
        bm = run.find("business_metric")
        if bm is not None:
            row["business_metric"] = bm.text
            
        # metrics
        for m in run.findall("metric"):
            name = m.get("name")
            if name:
                try:
                    row[name] = float(m.text) if m.text else None
                except (ValueError, TypeError):
                    row[name] = m.text
        
        # valid_run
        vr = run.find("valid_run")
        if vr is not None:
            row["valid_run"] = vr.text if vr.text else "VALID"
        else:
            row["valid_run"] = "VALID"
            
        data.append(row)
        
    return pd.DataFrame(data)


def read_xml(path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Read an XML summary file and extract achieved rate and average latency.
    """
    tree = ET.parse(path)
    root = tree.getroot()
    
    iops_list = []
    lat_list = []
    
    for run in root.findall("run"):
        metrics = {m.get("name"): m.text for m in run.findall("metric")}
        
        # 'achieved rate' corresponds to IOPS, 'average latency' to latency
        if "achieved rate" in metrics and "average latency" in metrics:
            try:
                iops_list.append(float(metrics["achieved rate"]))
                lat_list.append(float(metrics["average latency"]))
            except (ValueError, TypeError):
                continue
                
    iops = np.array(iops_list, dtype=float)
    latency = np.array(lat_list, dtype=float)
    half_dummy = np.zeros_like(latency)
    return iops, latency, half_dummy


def read_table(
    path: str,
    iops_col: Optional[Union[str, int]] = None,
    latency_col: Optional[Union[str, int]] = None,
    sheet: Optional[Union[str, int]] = None,
    delimiter: Optional[str] = None,
    header: Optional[Union[int, None]] = 0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Read a CSV, XLSX, or XML file and extract IOPS and latency columns.

    Returns: (iops_np, latency_np, half_latency_dummy)
    """
    ext = os.path.splitext(path)[1].lower()
    
    if ext == ".xml":
        return read_xml(path)
        
    _require_pandas()
    if ext in (".csv", ".tsv", ".txt"):
        df = pd.read_csv(path, delimiter=delimiter, header=header)
    elif ext in (".xlsx", ".xlsm", ".xls"):
        df = pd.read_excel(path, sheet_name=sheet, header=header)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")

    # For XML, columns were already identified. For others, use arguments.
    if iops_col is None or latency_col is None:
        raise ValueError(f"iops_col and latency_col are required for {ext} files")

    # Allow integer index or column name
