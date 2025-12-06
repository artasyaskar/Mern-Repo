import math
import requests

BASE = "http://localhost:3000"


def test_center_range_basic_positive_list():
    """center_range: computes min/max/mean/range for simple positive list."""
    r = requests.get(
        f"{BASE}/adv/center_range",
        params={"nums": "1,2,3,4"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"min": 1, "max": 4, "mean": 2.5, "range": 3}


def test_center_range_includes_negative_values():
    """center_range: handles negative and mixed-sign integers."""
    r = requests.get(
        f"{BASE}/adv/center_range",
        params={"nums": "-5,0,5"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data["min"] == -5
    assert data["max"] == 5
    assert math.isclose(data["mean"], 0.0, rel_tol=1e-9, abs_tol=1e-9)
    assert data["range"] == 10


def test_center_range_single_element_list():
    """center_range: single-element list returns that value for min/max/mean and range 0."""
    r = requests.get(
        f"{BASE}/adv/center_range",
        params={"nums": "42"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"min": 42, "max": 42, "mean": 42.0, "range": 0}


def test_center_range_empty_or_missing_nums_returns_400():
    """center_range: nums missing or empty should return HTTP 400."""
    for params in [
        {},
        {"nums": ""},
    ]:
        r = requests.get(f"{BASE}/adv/center_range", params=params, timeout=5)
        assert r.status_code == 400


def test_center_range_rejects_non_integer_tokens():
    """center_range: rejects clearly invalid tokens like letters or decimals."""
    for bad in [
        "1,2,x,4",   # letter
        "1,2,3.5",   # decimal
        "1,,2,3",    # empty token
    ]:
        r = requests.get(
            f"{BASE}/adv/center_range",
            params={"nums": bad},
            timeout=5,
        )
        assert r.status_code == 400


def test_center_range_ignores_trailing_spaces_only_when_part_of_valid_int():
    """center_range: simple whitespace handling around integers; invalid when not a number."""
    # A small positive example with spaces that still form valid integers.
    r_ok = requests.get(
        f"{BASE}/adv/center_range",
        params={"nums": " 1, 2 ,3 "},
        timeout=5,
    )
    assert r_ok.status_code == 200
    data = r_ok.json()
    assert data["min"] == 1 and data["max"] == 3

    # Clearly bad: token that is just spaces or cannot be parsed as int should 400.
    r_bad = requests.get(
        f"{BASE}/adv/center_range",
        params={"nums": "1, ,2"},
        timeout=5,
    )
    assert r_bad.status_code == 400
