import requests

BASE = "http://localhost:3000"


def test_phi_computes_correct_values_common_cases():
    """phi: computes Euler's totient using factorization (n=1,2,36)"""
    for n, expected in [(1, 1), (2, 1), (36, 12)]:
        r = requests.get(f"{BASE}/adv/phi", params={"n": n}, timeout=5)
        assert r.status_code == 200
        data = r.json()
        assert data == {"result": expected}


def test_phi_validates_positive_integer_only():
    """phi: rejects non-integers and non-positive inputs (strict integer validation)"""
    bad = [0, -5, 3.5, "10.0", None]
    for n in bad:
        r = requests.get(f"{BASE}/adv/phi", params={"n": n}, timeout=5)
        assert r.status_code == 400


def test_modinv_basic_and_negative_a_normalization():
    """modinv: extended gcd with normalization to [0,m-1], handles negative a"""
    r1 = requests.get(f"{BASE}/adv/modinv", params={"a": 3, "m": 11}, timeout=5)
    assert r1.status_code == 200 and r1.json() == {"result": 4}

    r2 = requests.get(f"{BASE}/adv/modinv", params={"a": -3, "m": 11}, timeout=5)
    assert r2.status_code == 200 and r2.json() == {"result": 7}


def test_modinv_non_coprime_returns_400():
    """modinv: when gcd(a,m) != 1 should return 400 with error"""
    r = requests.get(f"{BASE}/adv/modinv", params={"a": 6, "m": 9}, timeout=5)
    assert r.status_code == 400


def test_crt_solves_pair_smallest_non_negative_solution():
    """crt: solves system and returns smallest non-negative x and combined modulus"""
    payload = {"congruences": [
        {"a": 2, "m": 3},
        {"a": 3, "m": 5},
    ]}
    r = requests.post(f"{BASE}/adv/crt", json=payload, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data == {"x": 8, "modulus": 15}


def test_crt_validation_pairwise_coprime_and_shape():
    """crt: rejects invalid shapes and non pairwise-coprime moduli"""
    bad_payloads = [
        {},
        {"congruences": []},
        {"congruences": [{"a": 1}]},
        {"congruences": [{"a": 1, "m": 4}, {"a": 3, "m": 6}]},  # gcd(4,6) != 1
        {"congruences": [{"a": 1.2, "m": 5}, {"a": 2, "m": 3}]},
    ]
    for body in bad_payloads:
        r = requests.post(f"{BASE}/adv/crt", json=body, timeout=5)
        assert r.status_code == 400
