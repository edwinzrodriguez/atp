from __future__ import annotations

import argparse
import sys
from typing import Optional

import numpy as np

from .io import read_table
from .computation import find_knee_half_latency
from .output import write_text_report
from .plotting import plot_latency_curve


def positive_int(value: str) -> Optional[int]:
    if value is None:
        return None
    iv = int(value)
    if iv <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return iv


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Compute ATP (IOPS at knee) using the Half-Latency Rule and optionally plot results.",
    )
    p.add_argument("input", help="Path to input CSV/XLSX file")
    p.add_argument("--iops-col", required=True, help="Column name or index for IOPS")
    p.add_argument("--latency-col", required=True, help="Column name or index for latency")
    p.add_argument("--sheet", help="Sheet name or index for Excel files", default=None)
    p.add_argument("--delimiter", help="CSV delimiter (auto-detected by pandas if omitted)")
    p.add_argument("--header", help="Header row index (default 0); use 'none' for no header", default="0")
    p.add_argument("--rule", choices=["midrange", "double_min"], default="midrange", help="Half-latency rule")
    p.add_argument("--smooth", type=positive_int, default=None, help="Centered moving average window size for latency")
    p.add_argument("--latency-units", default="ms", help="Units label for latency values in reports and plots")
    p.add_argument("--report", help="Path to write text report; if omitted, prints to stdout")
    p.add_argument("--plot-pdf", help="Path to save plot as PDF")
    p.add_argument("--show", action="store_true", help="Show interactive plot window")
    p.add_argument("--title", help="Plot title")
    return p


def parse_col_arg(s: str):
    try:
        return int(s)
    except ValueError:
        return s


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    header: Optional[int]
    if args.header is None:
        header = 0
    elif isinstance(args.header, str) and args.header.lower() == "none":
        header = None
    else:
        header = int(args.header)

    iops_col = parse_col_arg(args.iops_col)
    latency_col = parse_col_arg(args.latency_col)
    sheet = None
    if args.sheet is not None:
        try:
            sheet = int(args.sheet)
        except ValueError:
            sheet = args.sheet

    iops, latency, _ = read_table(
        args.input,
        iops_col=iops_col,
        latency_col=latency_col,
        sheet=sheet,
        delimiter=args.delimiter,
        header=header,
    )

    res = find_knee_half_latency(iops, latency, rule=args.rule, smooth_window=args.smooth)

    write_text_report(iops, latency, res, out_path=args.report, latency_units=args.latency_units)

    if args.plot_pdf or args.show:
        plot_latency_curve(
            iops,
            latency,
            res,
            title=args.title,
            latency_units=args.latency_units,
            save_pdf=args.plot_pdf,
            show=args.show,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
