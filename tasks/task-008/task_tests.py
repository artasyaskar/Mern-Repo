import requests

BASE = "http://localhost:3000"


def test_prime_factors_basic_and_large_prime():
    """/adv/prime_factors returns nondecreasing prime factors; validates n>=2 integer."""
    r1 = requests.get(f"{BASE}/adv/prime_factors", params={"n": 60}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == [2, 2, 3, 5]

    # A prime stays as itself
    r2 = requests.get(f"{BASE}/adv/prime_factors", params={"n": 97}, timeout=5)
    assert r2.status_code == 200 and r2.json()["result"] == [97]


def test_prime_factors_validation():
    """/adv/prime_factors: reject non-integers and n<2."""
    for params in [
        {"n": 1},
        {"n": 0},
        {"n": -10},
        {"n": 2.5},
        {"n": "."},
    ]:
        r = requests.get(f"{BASE}/adv/prime_factors", params=params, timeout=5)
        assert r.status_code == 400


def test_rolling_median_basic_example_and_window_edges():
    """/adv/rolling_median computes medians over sliding windows; k odd and valid."""
    r1 = requests.get(
        f"{BASE}/adv/rolling_median",
        params={"nums": "1,3,2,6,4", "k": 3},
        timeout=5,
    )
    assert r1.status_code == 200 and r1.json()["result"] == [2, 3, 4]

    # k=1 returns original list
    r2 = requests.get(
        f"{BASE}/adv/rolling_median",
        params={"nums": "5,1,9", "k": 1},
        timeout=5,
    )
    assert r2.status_code == 200 and r2.json()["result"] == [5, 1, 9]


def test_rolling_median_validation():
    """/adv/rolling_median: rejects even k, too-large k, and bad lists."""
    for params in [
        {"nums": "1,2,3", "k": 2},
        {"nums": "1,2,3", "k": 5},
        {"nums": "1,,2", "k": 1},
        {"nums": "1,2.0,3", "k": 1},
        {"nums": "", "k": 1},
    ]:
        r = requests.get(f"{BASE}/adv/rolling_median", params=params, timeout=5)
        assert r.status_code == 400


def test_unique_mode_success_and_tie_is_400():
    """/adv/unique_mode returns unique most frequent or 400 on tie/no mode."""
    r1 = requests.get(f"{BASE}/adv/unique_mode", params={"nums": "1,2,2,3"}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 2

    # Tie between 2 and 3 -> 400
    r2 = requests.get(f"{BASE}/adv/unique_mode", params={"nums": "2,2,3,3"}, timeout=5)
    assert r2.status_code == 400


def test_unique_mode_validation_and_singleton():
    """/adv/unique_mode validates list and allows singleton (mode is the element)."""
    r1 = requests.get(f"{BASE}/adv/unique_mode", params={"nums": "1,2,3.5"}, timeout=5)
    assert r1.status_code == 400

    r2 = requests.get(f"{BASE}/adv/unique_mode", params={"nums": "42"}, timeout=5)
    assert r2.status_code == 200 and r2.json()["result"] == 42
