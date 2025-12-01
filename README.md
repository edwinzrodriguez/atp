# ATP – Half-Latency Knee Finder

ATP (Application Turning Point) analysis tools for computing the knee of a latency-vs-IOPS curve using the Half-Latency Rule. Includes utilities for reading input data (CSV/XLSX), computing ATP, producing a text report, and optional plotting.

## Install

- From source (this repo):
  - `pip install .`
  - Or with optional plotting deps: `pip install .[plot]`
  - For Excel .xlsx support: `pip install .[excel]`

## CLI Usage

- Basic (CSV with headers):
  `python -m atp --iops-col IOPS --latency-col Latency data.csv`

- Excel with a sheet name and save a PDF plot:
  `python -m atp data.xlsx --sheet "Run1" --iops-col 0 --latency-col 2 --plot-pdf result.pdf`

- Use the double_min rule and smoothing window of 3, write a text report:
  `python -m atp data.csv --iops-col IOPS --latency-col ms --rule double_min --smooth 3 --report atp_report.txt`

- Show interactive plot:
  `python -m atp data.csv --iops-col IOPS --latency-col Latency --show`

## Python API

- `find_knee_half_latency(iops, latency, rule="midrange", smooth_window=None)`
- `compute_half_latency(latency, rule="midrange")`

## Notes

- Dependencies: numpy, pandas. Optional: matplotlib (plots), openpyxl (Excel).
- The included paper (Half-Latency Rule for Finding the Knee of the Latency Curve.pdf) provides background for the method.
