import json
import math
import requests

BASE = "http://localhost:3000"


def test_quantiles_linear_basic_even_with_bounds():
    """quantiles: linear method with even N and full [0,25,50,75,100] percentiles"""
    payload = {
        "numbers": [1, 2, 3, 4],
        "method": "linear",
        "percentiles": [0, 25, 50, 75, 100],
    }
    r = requests.post(f"{BASE}/adv/quantiles", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # N=4, indices via i=(p/100)*(N-1): 0, 0.75, 1.5, 2.25, 3
    # values: 1, 1.75, 2.5, 3.25, 4
    assert data == {"0": 1, "25": 1.75, "50": 2.5, "75": 3.25, "100": 4}


def test_quantiles_tukey_odd_exclusive_median():
    """quantiles: tukey method excludes median from halves (odd N)"""
    payload = {
        "numbers": [1, 2, 3, 4, 5],
        "method": "tukey",
        "percentiles": [25, 50, 75],
    }
    r = requests.post(f"{BASE}/adv/quantiles", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # Sorted [1,2,3,4,5]; halves exclude median => lower [1,2], upper [4,5]
    # Q1=1.5, Q2=3, Q3=4.5
    assert data == {"25": 1.5, "50": 3, "75": 4.5}


def test_quantiles_validation_numbers_required_and_finite():
    """quantiles: invalid payloads rejected (missing/invalid numbers)"""
    bad_payloads = [
        {},
        {"numbers": [1, None]},
        {"numbers": ["a", 2]},
        {"numbers": [1]},  # length < 2
    ]
    for body in bad_payloads:
        r = requests.post(f"{BASE}/adv/quantiles", json=body, timeout=5)
        assert r.status_code == 400


def test_quantiles_percentiles_bounds_and_integers():
    """quantiles: percentiles must be integers in [0,100]"""
    bad_payloads = [
        {"numbers": [1, 2, 3], "percentiles": [25.5]},
        {"numbers": [1, 2, 3], "percentiles": [-1, 50, 101]},
        {"numbers": [1, 2, 3], "percentiles": ["50"]},
    ]
    for body in bad_payloads:
        r = requests.post(f"{BASE}/adv/quantiles", json=body, timeout=5)
        assert r.status_code == 400


def test_quantiles_defaults_and_sorting_tukey():
    """quantiles: defaults method=tukey and percentiles=[25,50,75] with sorting"""
    nums = [7, 1, 5, 3, 9]  # sorted -> [1,3,5,7,9]
    r = requests.post(f"{BASE}/adv/quantiles", json={"numbers": nums}, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # Tukey (odd N): lower [1,3] -> 2, median 5, upper [7,9] -> 8
    assert data == {"25": 2, "50": 5, "75": 8}


def test_quantiles_linear_numeric_stability_large_magnitudes():
    """quantiles: linear interpolation remains stable at ~1e12"""
    nums = [1_000_000_000_000, 1_000_000_000_001, 1_000_000_000_003, 1_000_000_000_006]
    payload = {"numbers": nums, "method": "linear", "percentiles": [50]}
    r = requests.post(f"{BASE}/adv/quantiles", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data == {"50": 1_000_000_000_002}


def test_quantiles_tukey_even_includes_split_halves():
    """quantiles: tukey method with even N splits halves evenly (median between middle two)"""
    payload = {
        "numbers": [1, 2, 3, 4, 5, 6],
        "method": "tukey",
        "percentiles": [25, 50, 75],
    }
    r = requests.post(f"{BASE}/adv/quantiles", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # Sorted [1,2,3,4,5,6]; halves include 3 elements each: lower [1,2,3], upper [4,5,6]
    # Q1=2, Q2=3.5, Q3=5
    assert data == {"25": 2, "50": 3.5, "75": 5}


def test_quantiles_invalid_method_rejected():
    """quantiles: invalid 'method' value should return 400"""
    payload = {
        "numbers": [1, 2, 3, 4],
        "method": "median",  # invalid
        "percentiles": [25, 50, 75],
    }
    r = requests.post(f"{BASE}/adv/quantiles", json=payload, timeout=5)
    assert r.status_code == 400
