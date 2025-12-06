import math
import time
import requests

BASE = "http://localhost:3000"


def test_rolling_stats_basic_window_size_3():
    """rolling_stats: computes mean/variance/stddev over sliding windows (k=3)."""
    r = requests.get(
        f"{BASE}/adv/rolling_stats",
        params={"nums": "1,2,3,4,5", "k": 3},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    # Windows: [1,2,3], [2,3,4], [3,4,5]
    # Means:   [2, 3, 4]
    # Sample variance (ddof=1): each window variance = 1.0, stddev = 1.0
    assert data["means"] == [2.0, 3.0, 4.0]
    assert all(abs(v - 1.0) < 1e-9 for v in data["variances"])
    assert all(abs(s - 1.0) < 1e-9 for s in data["stddevs"])


def test_rolling_stats_validation_nums_and_k():
    """rolling_stats: basic validation for nums and k."""
    # Keep validation minimal so implementation can be simple.
    for params in [
        {"nums": "", "k": 2},          # empty list
        {"nums": "1,2", "k": 3},      # k > len(nums)
        {"nums": "1,2,3", "k": 1},    # k < 2
    ]:
        r = requests.get(f"{BASE}/adv/rolling_stats", params=params, timeout=5)
        assert r.status_code == 400
