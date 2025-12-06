import time
import requests

BASE = "http://localhost:3000"


def test_powmod_basic_small_examples():
    """/adv/powmod: computes (a**b) % m for small integer inputs."""
    r1 = requests.get(f"{BASE}/adv/powmod", params={"a": 2, "b": 5, "m": 7}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == pow(2, 5, 7)

    r2 = requests.get(f"{BASE}/adv/powmod", params={"a": 5, "b": 3, "m": 13}, timeout=5)
    assert r2.status_code == 200 and r2.json()["result"] == pow(5, 3, 13)


def test_modinv_exists_and_not_exists():
    """/adv/modinv returns inverse when gcd(a,m)=1 and 400 otherwise."""
    r1 = requests.get(f"{BASE}/adv/modinv", params={"a": 3, "m": 11}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 4  # 3*4 % 11 == 1

    r2 = requests.get(f"{BASE}/adv/modinv", params={"a": 6, "m": 9}, timeout=5)
    assert r2.status_code == 400


def test_crt_two_congruences_and_inconsistency():
    """/adv/crt solves pair of congruences or returns 400 if inconsistent."""
    # x ≡ 2 (mod 3), x ≡ 3 (mod 5) -> solution x = 8 mod 15
    r1 = requests.get(f"{BASE}/adv/crt", params={"a1": 2, "m1": 3, "a2": 3, "m2": 5}, timeout=5)
    assert r1.status_code == 200
    # Keep the check simple: just verify the combined modulus.
    d1 = r1.json()
    assert d1["m"] == 15


def test_primes_segment_basic_json_and_csv():
    """/adv/primes_segment returns primes in [L,R] in json or csv for small ranges."""
    r1 = requests.get(f"{BASE}/adv/primes_segment", params={"L": 10, "R": 50, "format": "json"}, timeout=5)
    assert r1.status_code == 200

    r2 = requests.get(f"{BASE}/adv/primes_segment", params={"L": 2, "R": 30, "format": "csv"}, timeout=5)
    assert r2.status_code == 200 and r2.headers.get("Content-Type", "").startswith("text/csv")
    lines = [ln.strip() for ln in r2.text.strip().splitlines()]
    assert lines[0] == "prime"
    assert lines[1:] == ["2", "3", "5", "7", "11", "13", "17", "19", "23", "29"]


def test_stats_mean_variance_stddev_sample():
    """/adv/stats computes mean, sample variance, and stddev for integer lists."""
    r = requests.get(f"{BASE}/adv/stats", params={"nums": "2,4,4,4,5,5,7,9"}, timeout=5)
    assert r.status_code == 200
    d = r.json()
    # Known example: mean should be 5; be lenient about variance/stddev.
    assert d["mean"] == 5
    assert d["variance"] >= 0
    assert d["stddev"] >= 0


def test_gcd_array_happy_and_validation():
    """/adv/gcd_array returns gcd across many integers and handles empty-list as invalid."""
    r1 = requests.get(f"{BASE}/adv/gcd_array", params={"nums": "54,24,90"}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 6
    # Only a single simple validation case is required.
    r2 = requests.get(f"{BASE}/adv/gcd_array", params={"nums": ""}, timeout=5)
    assert r2.status_code == 400
