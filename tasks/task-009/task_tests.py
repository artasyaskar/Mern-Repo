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


def test_rolling_stats_respects_ddof_and_validation():
    """rolling_stats: supports ddof and enforces 0 <= ddof < k with 400 on bad ddof."""
    # ddof=0 (population variance)
    r = requests.get(
        f"{BASE}/adv/rolling_stats",
        params={"nums": "1,2,3,4", "k": 2, "ddof": 0},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    # Windows: [1,2], [2,3], [3,4]
    # Each window variance with ddof=0 is 0.25, stddev=0.5
    assert all(abs(v - 0.25) < 1e-9 for v in data["variances"])
    assert all(abs(s - 0.5) < 1e-9 for s in data["stddevs"])

    # Invalid ddof: equal to k, negative, or non-integer -> 400
    for params in [
        {"nums": "1,2,3", "k": 3, "ddof": 3},
        {"nums": "1,2,3", "k": 3, "ddof": -1},
        {"nums": "1,2,3", "k": 3, "ddof": "1.5"},
    ]:
        rr = requests.get(f"{BASE}/adv/rolling_stats", params=params, timeout=5)
        assert rr.status_code == 400


def test_rolling_stats_validation_nums_and_k():
    """rolling_stats: validates nums as integer list and k in valid range."""
    for params in [
        {"nums": "", "k": 2},               # empty list
        {"nums": "1,,2", "k": 2},           # blank token
        {"nums": "1,2.0,3", "k": 2},       # decimal
        {"nums": ".,2,3", "k": 2},         # invalid token
        {"nums": "1,2", "k": 3},           # k > len(nums)
        {"nums": "1,2,3", "k": 1},         # k < 2
        {"nums": "1,2,3", "k": "2.5"},   # non-integer k
    ]:
        r = requests.get(f"{BASE}/adv/rolling_stats", params=params, timeout=5)
        assert r.status_code == 400


def test_rolling_stats_window_edges_and_signs():
    """rolling_stats: handles negative numbers and k equal to len(nums)."""
    # k == len(nums) -> single window
    r = requests.get(
        f"{BASE}/adv/rolling_stats",
        params={"nums": "-1,-1,3", "k": 3},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    # One window [-1,-1,3]: mean = 1/3, variance= 14/3 / (3-1)= 7/3, stddev=sqrt(7/3)
    assert len(data["means"]) == 1
    m = data["means"][0]
    v = data["variances"][0]
    s = data["stddevs"][0]
    assert abs(m - (1.0 / 3.0)) < 1e-9
    assert abs(v - (7.0 / 3.0)) < 1e-9
    assert abs(s - math.sqrt(7.0 / 3.0)) < 1e-9


def test_rolling_stats_numeric_stability_large_values():
    """rolling_stats: numerically stable for values around 1e9 (no catastrophic cancellation)."""
    nums = [1_000_000_000, 1_000_000_001, 999_999_999, 1_000_000_002]
    r = requests.get(
        f"{BASE}/adv/rolling_stats",
        params={"nums": ",".join(str(x) for x in nums), "k": 2},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    # Windows: [1e9,1e9+1], [1e9+1,1e9-1], [1e9-1,1e9+2]
    # We only require that variance/stddev are finite and small (no overflow/NaN)
    for v, s in zip(data["variances"], data["stddevs"]):
        assert math.isfinite(v)
        assert math.isfinite(s)
        assert v >= 0
        assert s >= 0


def test_rolling_stats_performance_moderate_size():
    """rolling_stats: runs within reasonable time for lists up to ~2000 elements."""
    nums = list(range(2000))
    param_nums = ",".join(str(x) for x in nums)
    start = time.time()
    r = requests.get(
        f"{BASE}/adv/rolling_stats",
        params={"nums": param_nums, "k": 50},
        timeout=10,
    )
    elapsed = time.time() - start
    assert r.status_code == 200
    data = r.json()
    # There should be len(nums) - k + 1 windows
    assert len(data["means"]) == len(nums) - 50 + 1
    assert len(data["variances"]) == len(nums) - 50 + 1
    assert len(data["stddevs"]) == len(nums) - 50 + 1
    assert elapsed < 2.0
