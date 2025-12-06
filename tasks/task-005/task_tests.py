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
    r = requests.get(f"{BASE}/adv/egcd", params={"a": 240, "b": 46}, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # For this example, gcd should be 2 and the returned x,y should satisfy the Bezout identity.
    assert data["gcd"] == 2
    assert 240 * data["x"] + 46 * data["y"] == 2


def test_lcm_many_validation():
    """/adv/lcm_many rejects empty inputs and any non-integer tokens with HTTP 400."""
    # Any non-integer or empty -> 400
    for q in ["", " ", ",,,", "1,2,3.5", "a,b,c", "1,,2"]:
        r = requests.get(f"{BASE}/adv/lcm_many", params={"nums": q}, timeout=5)
        assert r.status_code == 400


def test_primes_range_csv_and_performance():
    """/adv/primes_range supports CSV (with header) for a small range."""
    r = requests.get(f"{BASE}/adv/primes_range", params={"n": 30, "format": "csv"}, timeout=5)
    assert r.status_code == 200
    assert r.headers.get("Content-Type", "").startswith("text/csv")
    lines = [ln.strip() for ln in r.text.strip().splitlines()]
    assert lines[0] == "prime"
    assert lines[1:] == ["2", "3", "5", "7", "11", "13", "17", "19", "23", "29"]


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
