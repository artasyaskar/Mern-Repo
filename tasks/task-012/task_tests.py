import requests

BASE = "http://localhost:3000"


def test_reverse_list_basic_positive_list():
    """reverse_list: returns the list reversed for a simple positive list."""
    r = requests.get(
        f"{BASE}/adv/reverse_list",
        params={"nums": "1,2,3,4"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"reversed": [4, 3, 2, 1]}


def test_reverse_list_includes_negative_and_zero():
    """reverse_list: reverses correctly with negative numbers and zero."""
    r = requests.get(
        f"{BASE}/adv/reverse_list",
        params={"nums": "-2,0,5"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"reversed": [5, 0, -2]}


def test_reverse_list_single_number():
    """reverse_list: single number returns the same number in a list."""
    r = requests.get(
        f"{BASE}/adv/reverse_list",
        params={"nums": "7"},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"reversed": [7]}


def test_reverse_list_whitespace_handling():
    """reverse_list: trims spaces around valid integers and reverses them."""
    r = requests.get(
        f"{BASE}/adv/reverse_list",
        params={"nums": " 1, 2 ,3 "},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    assert data == {"reversed": [3, 2, 1]}


def test_reverse_list_empty_or_missing_nums_returns_400():
    """reverse_list: nums missing or empty should return HTTP 400."""
    for params in [
        {},
        {"nums": ""},
    ]:
        r = requests.get(f"{BASE}/adv/reverse_list", params=params, timeout=5)
        assert r.status_code == 400


def test_reverse_list_rejects_non_integer_tokens():
    """reverse_list: rejects clearly invalid tokens like letters or decimals."""
    for bad in [
        "1,2,x,4",   # letter
        "1,2,3.5",   # decimal
        "1,,2,3",    # empty token
    ]:
        r = requests.get(
            f"{BASE}/adv/reverse_list",
            params={"nums": bad},
            timeout=5,
        )
        assert r.status_code == 400
