import math
import requests

BASE = "http://localhost:3000"


def test_percentile_nearest_rank_basic_and_edges():
    """/adv/percentile uses nearest-rank on integer list; handles p=0 and p=100 edges."""
    # Basic
    r1 = requests.get(f"{BASE}/adv/percentile", params={"nums": "1,2,3,4", "p": 75}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == 3

    # p=0 -> rank=1 -> min value
    r2 = requests.get(f"{BASE}/adv/percentile", params={"nums": "10,20,30", "p": 0}, timeout=5)
    assert r2.status_code == 200 and r2.json()["result"] == 10

    # p=100 -> max value
    r3 = requests.get(f"{BASE}/adv/percentile", params={"nums": "-5,0,5", "p": 100}, timeout=5)
    assert r3.status_code == 200 and r3.json()["result"] == 5


def test_convolve_basic_example_and_signs():
    """/adv/convolve computes full linear convolution correctly (example and negative values)."""
    r1 = requests.get(f"{BASE}/adv/convolve", params={"a": "1,2,3", "b": "4,5"}, timeout=5)
    assert r1.status_code == 200 and r1.json()["result"] == [4, 13, 22, 15]

    r2 = requests.get(f"{BASE}/adv/convolve", params={"a": "2,-1", "b": "3,0,1"}, timeout=5)
    # Manual conv: [2*3, 2*0+(-1)*3, 2*1+(-1)*0, (-1)*1] -> [6, -3, 2, -1]
    assert r2.status_code == 200 and r2.json()["result"] == [6, -3, 2, -1]


def test_mmm_mean_median_mode_typical():
    """/adv/mmm returns mean (float), median, and mode for integer list."""
    r = requests.get(f"{BASE}/adv/mmm", params={"nums": "2,4,4,4,5,5,7,9"}, timeout=5)
    assert r.status_code == 200
    d = r.json()
    assert abs(d["mean"] - 5.0) < 1e-9
    assert d["median"] == 4.5
    assert d["mode"] == 4


def test_mmm_validation_and_singleton():
    """/adv/mmm validates input and handles singleton arrays."""
    r1 = requests.get(f"{BASE}/adv/mmm", params={"nums": "1,2,3.1"}, timeout=5)
    assert r1.status_code == 400

    r2 = requests.get(f"{BASE}/adv/mmm", params={"nums": "42"}, timeout=5)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["mean"] == 42
    assert d2["median"] == 42
    assert d2["mode"] == 42
