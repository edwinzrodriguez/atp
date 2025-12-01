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

- Compare two datasets (report absolute and % differences, plus overlay plot):
  `python -m atp dataA.csv --iops-col IOPS --latency-col Latency --compare dataB.csv --iops-col2 IOPS --latency-col2 Latency --label1 A --label2 B --plot-pdf compare.pdf`

  Notes:
  - If `--iops-col2` / `--latency-col2` are omitted, the first dataset's column settings are reused.
  - `--sheet2`, `--header2`, and `--delimiter2` allow specifying parsing for the second file.
  - The generated report includes absolute and percentage differences for ATP (IOPS at knee) and knee latency.

## Python API

- `find_knee_half_latency(iops, latency, rule="midrange", smooth_window=None)`
- `compute_half_latency(latency, rule="midrange")`

## Notes

- Dependencies: numpy, pandas. Optional: matplotlib (plots), openpyxl (Excel).
- The included paper (Half-Latency Rule for Finding the Knee of the Latency Curve.pdf) provides background for the method.
