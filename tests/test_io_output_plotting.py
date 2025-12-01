import io
import os

import numpy as np
import pytest


pd = pytest.importorskip("pandas")


def test_read_table_csv(tmp_path):
    from atp.io import read_table

    # Create a simple CSV
    p = tmp_path / "data.csv"
    p.write_text("IOPS,Latency,Other\n100,1.0,x\n200,2.0,y\n", encoding="utf-8")

    iops, lat, half = read_table(str(p), iops_col="IOPS", latency_col="Latency")
    assert iops.tolist() == [100.0, 200.0]
    assert lat.tolist() == [1.0, 2.0]
    assert np.all(half == 0)


def test_write_text_report_creates_expected_lines(tmp_path):
    from atp.output import write_text_report
    from atp.computation import KneeResult

    iops = np.array([100.0, 200.0, 300.0])
    lat = np.array([1.0, 2.0, 4.0])
    res = KneeResult(atp_iops=250.0, knee_latency=3.0, half_latency=3.0, knee_index_left=1, knee_index_right=2)

    out = tmp_path / "report.txt"
    write_text_report(iops, lat, res, out_path=str(out), latency_units="ms")
    text = out.read_text(encoding="utf-8")
    assert "ATP Analysis Report" in text
    assert "Half-latency: 3.000 ms" in text
    assert "Knee latency: 3.000 ms" in text
    assert "ATP (IOPS at knee): 250.000" in text
    # Should list rows with third column equal to half-latency
    assert "100.000, 1.000, 3.000" in text


def test_plot_latency_curve_saves_pdf(tmp_path):
    plt = pytest.importorskip("matplotlib.pyplot")
    from atp.plotting import plot_latency_curve
    from atp.computation import KneeResult

    iops = np.array([100.0, 200.0, 300.0])
    lat = np.array([1.0, 2.0, 4.0])
    res = KneeResult(atp_iops=200.0, knee_latency=2.0, half_latency=2.0, knee_index_left=0, knee_index_right=1)

    pdf_path = tmp_path / "plot.pdf"
    plot_latency_curve(iops, lat, res, title="Test", save_pdf=str(pdf_path), show=False)
    assert pdf_path.exists() and pdf_path.stat().st_size > 0
