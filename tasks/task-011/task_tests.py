import math
import requests

BASE = "http://localhost:3000"


def test_sum_stats_basic_positive_list():
    """sum_stats: reports count/sum/average for a simple positive list."""
    r = requests.get(
        f"{BASE}/adv/sum_stats",
        params={"nums": "1,2,3,4"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"count": 4, "sum": 10, "average": 2.5}


def test_sum_stats_includes_negative_values():
    """sum_stats: handles negative and non-negative integers together."""
    r = requests.get(
        f"{BASE}/adv/sum_stats",
        params={"nums": "-2,0,5"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 3
    assert data["sum"] == 3
    assert math.isclose(data["average"], 1.0, rel_tol=1e-9, abs_tol=1e-9)


def test_sum_stats_single_value():
    """sum_stats: single value list reports count=1, sum=value, average=float(value)."""
    r = requests.get(
        f"{BASE}/adv/sum_stats",
        params={"nums": "10"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"count": 1, "sum": 10, "average": 10.0}


def test_sum_stats_empty_or_missing_nums_returns_400():
    """sum_stats: nums missing or empty should return HTTP 400."""
    for params in [
        {},
        {"nums": ""},
    ]:
        r = requests.get(f"{BASE}/adv/sum_stats", params=params, timeout=5)
        assert r.status_code == 400


def test_sum_stats_rejects_non_integer_tokens():
    """sum_stats: rejects clearly invalid tokens like letters or decimals."""
    for bad in [
        "1,2,x,4",   # letter
        "1,2,3.5",   # decimal
        "1,,2,3",    # empty token
    ]:
        r = requests.get(
            f"{BASE}/adv/sum_stats",
            params={"nums": bad},
            timeout=5,
        )
        assert r.status_code == 400


def test_sum_stats_whitespace_handling_valid_and_invalid():
    """sum_stats: trims spaces around valid integers and rejects tokens that are just spaces."""
    # Valid with spaces around proper integers.
    r_ok = requests.get(
        f"{BASE}/adv/sum_stats",
        params={"nums": " 1, 2 ,3 "},
        timeout=5,
    )
    assert r_ok.status_code == 200
    data = r_ok.json()
    assert data["count"] == 3
    assert data["sum"] == 6
    assert math.isclose(data["average"], 2.0, rel_tol=1e-9, abs_tol=1e-9)

    # Clearly bad: token that is just spaces should 400.
    r_bad = requests.get(
        f"{BASE}/adv/sum_stats",
        params={"nums": "1, ,2"},
        timeout=5,
    )
    assert r_bad.status_code == 400
