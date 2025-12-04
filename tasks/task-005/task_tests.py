import json
import time
import requests

BASE = "http://localhost:3000"


def test_gcd_lcm_require_integers_and_signs_normalized():
    # Non-integers must be rejected (current impl accepts floats -> should fail until fixed)
    r1 = requests.get(f"{BASE}/adv/gcd", params={"a": 8.5, "b": 12}, timeout=5)
    r2 = requests.get(f"{BASE}/adv/lcm", params={"a": -4.2, "b": 6}, timeout=5)
    assert r1.status_code == 400
    assert r2.status_code == 400

    # Valid negative integers produce non-negative results
    r3 = requests.get(f"{BASE}/adv/gcd", params={"a": -8, "b": 12}, timeout=5)
    r4 = requests.get(f"{BASE}/adv/lcm", params={"a": -4, "b": 6}, timeout=5)
    assert r3.status_code == 200 and r3.json()["result"] == 4
    assert r4.status_code == 200 and r4.json()["result"] == 12


def test_egcd_endpoint_returns_bezout_coefficients():
    # New endpoint; should be 404 before implementation (ensures failing first run)
    r = requests.get(f"{BASE}/adv/egcd", params={"a": 240, "b": 46}, timeout=5)
    # After implementation: gcd=2, one solution is x = -9, y = 47 (240*(-9) + 46*47 = 2)
    assert r.status_code == 200
    data = r.json()
    assert data["gcd"] == 2
    assert 240 * data["x"] + 46 * data["y"] == 2


def test_lcm_many_happy_path_and_zero():
    # New endpoint; initially 404 -> failing
    r1 = requests.get(f"{BASE}/adv/lcm_many", params={"nums": "-4,6,8"}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 24

    r2 = requests.get(f"{BASE}/adv/lcm_many", params={"nums": "5,0,10"}, timeout=5)
    assert r2.status_code == 200 and r2.json()["result"] == 0


def test_lcm_many_validation():
    # Any non-integer or empty -> 400
    for q in ["", " ", ",,,", "1,2,3.5", "a,b,c", "1,,2"]:
        r = requests.get(f"{BASE}/adv/lcm_many", params={"nums": q}, timeout=5)
        assert r.status_code == 400


def test_primes_range_json_start_bound():
    # New endpoint for ranged primes and formats; initially 404 -> failing
    r = requests.get(
        f"{BASE}/adv/primes_range",
        params={"n": 50, "start": 10, "format": "json"},
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json() == {"result": [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]}


def test_primes_range_csv_and_performance():
    # CSV format with header
    r = requests.get(f"{BASE}/adv/primes_range", params={"n": 30, "format": "csv"}, timeout=5)
    assert r.status_code == 200
    assert r.headers.get("Content-Type", "").startswith("text/csv")
    lines = [ln.strip() for ln in r.text.strip().splitlines()]
    assert lines[0] == "prime"
    assert lines[1:] == ["2", "3", "5", "7", "11", "13", "17", "19", "23", "29"]

    # Performance up to 30000 in < 2s using json
    start = time.time()
    r2 = requests.get(f"{BASE}/adv/primes_range", params={"n": 30000, "format": "json"}, timeout=10)
    elapsed = time.time() - start
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data.get("result"), list)
    assert len(data["result"]) == 3245  # pi(30000) = 3245
    assert elapsed < 2.0
