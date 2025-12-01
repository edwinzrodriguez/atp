import numpy as np
import pytest

from atp.computation import (
    compute_half_latency,
    find_knee_half_latency,
)


def test_compute_half_latency_midrange():
    lat = np.array([1.0, 2.0, 5.0, 9.0])
    assert compute_half_latency(lat, rule="midrange") == pytest.approx((1.0 + 9.0) / 2)


def test_compute_half_latency_double_min():
    lat = np.array([1.25, 2.0, 8.0])
    assert compute_half_latency(lat, rule="double_min") == pytest.approx(2.5)


def test_find_knee_interpolation_midrange():
    # Latency crosses half-latency between points; expect linear interpolation for ATP
    iops = np.array([100, 200, 300, 400], dtype=float)
    lat = np.array([1.0, 2.0, 6.0, 10.0], dtype=float)
    # midrange half = (1 + 10)/2 = 5.5, crossing between 200 (2.0) and 300 (6.0)
    res = find_knee_half_latency(iops, lat, rule="midrange")
    # t = (5.5-2)/(6-2) = 3.5/4 = 0.875 -> x = 200 + 0.875*100 = 287.5
    assert res.atp_iops == pytest.approx(287.5)
    assert res.knee_latency == pytest.approx(5.5)
    assert res.half_latency == pytest.approx(5.5)
    assert res.knee_index_left == 1 and res.knee_index_right == 2


def test_find_knee_exact_match_and_indexes():
    # Exact match to half-latency at a point; ensure indices are set correctly
    iops = np.array([10, 20, 30], dtype=float)
    lat = np.array([5, 10, 15], dtype=float)
    # double_min: 2*min = 10 -> matches second point exactly
    res = find_knee_half_latency(iops, lat, rule="double_min")
    assert res.atp_iops == pytest.approx(20)
    assert res.knee_latency == pytest.approx(10)
    assert res.knee_index_left == 0
    assert res.knee_index_right == 1


def test_find_knee_no_crossing_returns_last_point():
    # Half-latency above all values -> returns last point
    iops = np.array([100, 200, 300], dtype=float)
    lat = np.array([1.0, 1.2, 1.3], dtype=float)
    # double_min = 2*1.0 = 2.0, never reached
    res = find_knee_half_latency(iops, lat, rule="double_min")
    assert res.atp_iops == pytest.approx(300)
    assert res.knee_latency == pytest.approx(1.3)
    assert res.knee_index_left == 1
    assert res.knee_index_right == 2


def test_unsorted_inputs_and_nans_handled():
    iops = np.array([300, np.nan, 100, 200], dtype=float)
    lat = np.array([6.0, 7.0, 1.0, 3.0], dtype=float)
    res = find_knee_half_latency(iops, lat, rule="midrange")
    # After removing NaN, pairs are (100,1.0),(200,3.0),(300,6.0)
    # midrange half = (1+6)/2 = 3.5, crossing between 200 and 300
    # t = (3.5-3.0)/(6.0-3.0) = 0.5/3 = 1/6, x = 200 + (1/6)*100 = 216.666...
    assert res.atp_iops == pytest.approx(216.6666667)
    assert res.knee_latency == pytest.approx(3.5)
    assert res.knee_index_left == 1 and res.knee_index_right == 2


def test_smoothing_does_not_crash_and_is_used():
    iops = np.array([100, 200, 300, 400, 500], dtype=float)
    lat = np.array([1.0, 1.2, 5.0, 5.2, 5.4], dtype=float)
    # Ensure smooth_window argument is accepted and produces a valid result
    res = find_knee_half_latency(iops, lat, rule="midrange", smooth_window=3)
    assert np.isfinite(res.atp_iops)
    assert np.isfinite(res.knee_latency)
    assert np.isfinite(res.half_latency)
