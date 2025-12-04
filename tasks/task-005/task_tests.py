import json
import time
import requests

BASE = "http://localhost:3000"


def test_gcd_lcm_require_integers_and_signs_normalized():
    """/adv/gcd and /adv/lcm must reject non-integers (HTTP 400) and normalize signs to non-negative results."""
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

    # Additional varied cases (anti-cheating: multiple inputs not just a single pair)
    r5 = requests.get(f"{BASE}/adv/gcd", params={"a": 54, "b": 24}, timeout=5)
    r6 = requests.get(f"{BASE}/adv/lcm", params={"a": 21, "b": 6}, timeout=5)
    assert r5.status_code == 200 and r5.json()["result"] == 6
    assert r6.status_code == 200 and r6.json()["result"] == 42


def test_egcd_endpoint_returns_bezout_coefficients():
    """/adv/egcd returns gcd and one pair of Bezout coefficients (x,y) such that ax+by=gcd(a,b)."""
    # New endpoint; should be 404 before implementation (ensures failing first run)
    r = requests.get(f"{BASE}/adv/egcd", params={"a": 240, "b": 46}, timeout=5)
    # After implementation: gcd=2, one solution is x = -9, y = 47 (240*(-9) + 46*47 = 2)
    assert r.status_code == 200
    data = r.json()
    assert data["gcd"] == 2
    assert 240 * data["x"] + 46 * data["y"] == 2

    # Additional pairs to reduce trivial hardcoding
    for a, b in [(99, 78), (101, 103), (-56, 15)]:
        rr = requests.get(f"{BASE}/adv/egcd", params={"a": a, "b": b}, timeout=5)
        assert rr.status_code == 200
        dd = rr.json()
        G = dd["gcd"]
        # gcd must be non-negative and divide both
        assert G >= 0 and a % G == 0 and b % G == 0
        assert a * dd["x"] + b * dd["y"] == G


def test_lcm_many_happy_path_and_zero():
    """/adv/lcm_many computes LCM across many integers, handling negatives and zero."""
    # New endpoint; initially 404 -> failing
    r1 = requests.get(f"{BASE}/adv/lcm_many", params={"nums": "-4,6,8"}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 24

    r2 = requests.get(f"{BASE}/adv/lcm_many", params={"nums": "5,0,10"}, timeout=5)
    assert r2.status_code == 200 and r2.json()["result"] == 0

    # Additional varied cases
    r3 = requests.get(f"{BASE}/adv/lcm_many", params={"nums": "7,14,21"}, timeout=5)
    r4 = requests.get(f"{BASE}/adv/lcm_many", params={"nums": "3,5,15,30"}, timeout=5)
    assert r3.status_code == 200 and r3.json()["result"] == 42
    assert r4.status_code == 200 and r4.json()["result"] == 30


def test_lcm_many_validation():
    """/adv/lcm_many rejects empty inputs and any non-integer tokens with HTTP 400."""
    # Any non-integer or empty -> 400
    for q in ["", " ", ",,,", "1,2,3.5", "a,b,c", "1,,2"]:
        r = requests.get(f"{BASE}/adv/lcm_many", params={"nums": q}, timeout=5)
        assert r.status_code == 400


def test_primes_range_json_start_bound():
    """/adv/primes_range returns primes up to n, optionally filtered by start, as JSON array."""
    # New endpoint for ranged primes and formats; initially 404 -> failing
    r = requests.get(
        f"{BASE}/adv/primes_range",
        params={"n": 50, "start": 10, "format": "json"},
        timeout=5,
    )
    assert r.status_code == 200
    assert r.json() == {"result": [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]}


def test_primes_range_csv_and_performance():
    """/adv/primes_range supports CSV (with header) and performs within 2s for n=30000 in JSON mode."""
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


def test_egcd_requires_integers():
    """/adv/egcd must reject non-integer inputs with HTTP 400."""
    r1 = requests.get(f"{BASE}/adv/egcd", params={"a": 7.5, "b": 5}, timeout=5)
    r2 = requests.get(f"{BASE}/adv/egcd", params={"a": 12, "b": -3.2}, timeout=5)
    assert r1.status_code == 400
    assert r2.status_code == 400


def test_literal_dot_tokens_rejected_for_integer_endpoints():
    """Endpoints that require integers must reject a literal '.' token in query params."""
    for path, params in [
        ("/adv/gcd", {"a": ".", "b": "12"}),
        ("/adv/lcm", {"a": ".", "b": "6"}),
        ("/adv/egcd", {"a": ".", "b": "5"}),
    ]:
        r = requests.get(f"{BASE}{path}", params=params, timeout=5)
        assert r.status_code == 400
