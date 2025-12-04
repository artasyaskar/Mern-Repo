import time
import requests

BASE = "http://localhost:3000"


def test_powmod_validation_and_large_exponent():
    """/adv/powmod: integer-only, b>=0, m>1; handles large exponents efficiently."""
    # Missing/invalid -> 400
    for params in [
        {"a": 2.5, "b": 10, "m": 7},
        {"a": 2, "b": -1, "m": 7},
        {"a": 2, "b": 10, "m": 1},
        {"a": ".", "b": "10", "m": "7"},
    ]:
        r = requests.get(f"{BASE}/adv/powmod", params=params, timeout=5)
        assert r.status_code == 400

    # Happy path and performance (should be very fast with fast power)
    start = time.time()
    r2 = requests.get(f"{BASE}/adv/powmod", params={"a": 123456789, "b": 10000000, "m": 100000007}, timeout=10)
    elapsed = time.time() - start
    assert r2.status_code == 200
    # Numeric correctness and performance
    assert r2.json()["result"] == pow(123456789, 10000000, 100000007)
    assert elapsed < 1.0

    # Additional correctness check with smaller numbers
    r3 = requests.get(f"{BASE}/adv/powmod", params={"a": 5, "b": 117, "m": 19}, timeout=5)
    assert r3.status_code == 200 and r3.json()["result"] == pow(5, 117, 19)


def test_modinv_exists_and_not_exists():
    """/adv/modinv returns inverse when gcd(a,m)=1 and 400 otherwise."""
    r1 = requests.get(f"{BASE}/adv/modinv", params={"a": 3, "m": 11}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 4  # 3*4 % 11 == 1

    r2 = requests.get(f"{BASE}/adv/modinv", params={"a": 6, "m": 9}, timeout=5)
    assert r2.status_code == 400

    # Validation
    r3 = requests.get(f"{BASE}/adv/modinv", params={"a": 2.2, "m": 5}, timeout=5)
    assert r3.status_code == 400


def test_crt_two_congruences_and_inconsistency():
    """/adv/crt solves pair of congruences or returns 400 if inconsistent."""
    # x ≡ 2 (mod 3), x ≡ 3 (mod 5) -> solution x = 8 mod 15
    r1 = requests.get(f"{BASE}/adv/crt", params={"a1": 2, "m1": 3, "a2": 3, "m2": 5}, timeout=5)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["m"] == 15 and d1["x"] % 3 == 2 and d1["x"] % 5 == 3 and 0 <= d1["x"] < d1["m"]

    # Inconsistent: x ≡ 1 (mod 2), x ≡ 0 (mod 2)
    r2 = requests.get(f"{BASE}/adv/crt", params={"a1": 1, "m1": 2, "a2": 0, "m2": 2}, timeout=5)
    assert r2.status_code == 400

    # Validation
    r3 = requests.get(f"{BASE}/adv/crt", params={"a1": ".", "m1": "3", "a2": "3", "m2": "5"}, timeout=5)
    assert r3.status_code == 400


def test_primes_segment_json_and_csv_and_performance():
    """/adv/primes_segment returns primes in [L,R] with json/csv formats and meets perf target."""
    r1 = requests.get(f"{BASE}/adv/primes_segment", params={"L": 10, "R": 50, "format": "json"}, timeout=5)
    assert r1.status_code == 200
    assert r1.json() == {"result": [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]}

    r2 = requests.get(f"{BASE}/adv/primes_segment", params={"L": 2, "R": 30, "format": "csv"}, timeout=5)
    assert r2.status_code == 200 and r2.headers.get("Content-Type", "").startswith("text/csv")
    lines = [ln.strip() for ln in r2.text.strip().splitlines()]
    assert lines[0] == "prime"
    assert lines[1:] == ["2", "3", "5", "7", "11", "13", "17", "19", "23", "29"]

    # Performance up to 100000 in < 1.5s json
    start = time.time()
    r3 = requests.get(f"{BASE}/adv/primes_segment", params={"L": 2, "R": 100000, "format": "json"}, timeout=15)
    elapsed = time.time() - start
    assert r3.status_code == 200
    data = r3.json()
    assert isinstance(data.get("result"), list)
    assert elapsed < 1.5


def test_stats_mean_variance_stddev_sample():
    """/adv/stats computes mean, sample variance, and stddev for integer lists."""
    r = requests.get(f"{BASE}/adv/stats", params={"nums": "2,4,4,4,5,5,7,9"}, timeout=5)
    assert r.status_code == 200
    d = r.json()
    # Known example: mean 5, sample variance 4, stddev 2
    assert d["mean"] == 5
    assert abs(d["variance"] - 4) < 1e-9
    assert abs(d["stddev"] - 2) < 1e-9

    # Validation
    r2 = requests.get(f"{BASE}/adv/stats", params={"nums": "1,2,3.5"}, timeout=5)
    assert r2.status_code == 400


def test_gcd_array_happy_and_validation():
    """/adv/gcd_array returns gcd across many integers and validates input list."""
    r1 = requests.get(f"{BASE}/adv/gcd_array", params={"nums": "54,24,90"}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 6

    r2 = requests.get(f"{BASE}/adv/gcd_array", params={"nums": ""}, timeout=5)
    assert r2.status_code == 400
    r3 = requests.get(f"{BASE}/adv/gcd_array", params={"nums": "1,,2"}, timeout=5)
    assert r3.status_code == 400
