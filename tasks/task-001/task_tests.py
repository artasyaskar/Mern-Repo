import json
import math
import time
import requests

BASE = "http://localhost:3000"


def test_stats_basic_sample_variance_and_stddev():
    payload = {"numbers": [1, 2, 3, 4, 5]}
    r = requests.post(f"{BASE}/adv/stats", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data["mean"] == 3
    assert data["median"] == 3
    assert data["mode"] == 3
    assert abs(data["variance"] - 2.5) < 1e-9
    assert abs(data["stddev"] - math.sqrt(2.5)) < 1e-9


def test_stats_ddof_and_validation():
    # ddof default = 1; ddof too large should 400
    r = requests.post(f"{BASE}/adv/stats", json={"numbers": [10, 10], "ddof": 2}, timeout=5)
    assert r.status_code == 400
    # invalid payloads
    # Use null instead of Infinity to keep JSON serializable while still invalid for server
    for body in [{}, {"numbers": []}, {"numbers": [1, None]}]:
        rr = requests.post(f"{BASE}/adv/stats", json=body, timeout=5)
        assert rr.status_code == 400


def test_primes_with_start_and_json_format():
    r = requests.get(f"{BASE}/adv/primes", params={"n": 20, "start": 10, "format": "json"}, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data == {"result": [11, 13, 17, 19]}


def test_primes_with_csv_format_and_content_type():
    r = requests.get(f"{BASE}/adv/primes", params={"n": 15, "format": "csv"}, timeout=5)
    assert r.status_code == 200
    assert r.headers.get("Content-Type", "").startswith("text/csv")
    lines = [ln.strip() for ln in r.text.strip().splitlines()]
    assert lines[0] == "prime"
    assert lines[1:] == ["2", "3", "5", "7", "11", "13"]


def test_primes_invalid_range_returns_400():
    r = requests.get(f"{BASE}/adv/primes", params={"n": 10, "start": 12}, timeout=5)
    assert r.status_code == 400


def test_gcd_lcm_require_integers_and_non_negative():
    # inputs must be integers; decimal inputs should be rejected
    r1 = requests.get(f"{BASE}/adv/gcd", params={"a": 8.5, "b": 12}, timeout=5)
    r2 = requests.get(f"{BASE}/adv/lcm", params={"a": -4.2, "b": 6}, timeout=5)
    assert r1.status_code == 400
    assert r2.status_code == 400

    # valid negative integers produce non-negative results
    r3 = requests.get(f"{BASE}/adv/gcd", params={"a": -8, "b": 12}, timeout=5)
    r4 = requests.get(f"{BASE}/adv/lcm", params={"a": -4, "b": 6}, timeout=5)
    assert r3.status_code == 200 and r3.json()["result"] == 4
    assert r4.status_code == 200 and r4.json()["result"] == 12
