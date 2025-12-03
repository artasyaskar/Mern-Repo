import time
import requests
import pytest
import json

BASE_URL = "http://localhost:3000"


def post_json(path, body, timeout=5):
    return requests.post(BASE_URL + path, json=body, timeout=timeout)


def test_sets_and_uses_variables_across_requests():
    r1 = post_json('/api/vars', {"name": "x", "value": 3})
    assert r1.status_code == 200
    r2 = post_json('/api/vars', {"name": "y", "value": 4})
    assert r2.status_code == 200
    r3 = post_json('/api/calc', {"expr": "x*y + 2"})
    assert r3.status_code == 200
    assert r3.json()["result"] == 14


def test_parentheses_and_precedence():
    r = post_json('/api/calc', {"expr": "2 + 3 * 4 - (5 - 1) * 2"})
    assert r.status_code == 200
    assert r.json()["result"] == 2 + 12 - (4) * 2


def test_unary_minus_and_nested_parentheses():
    r = post_json('/api/calc', {"expr": "-(2 + 3) * (4 + -(1))"})
    assert r.status_code == 200
    assert r.json()["result"] == -(5) * (3)


def test_division_by_zero_error():
    r = post_json('/api/calc', {"expr": "10 / (5-5)"})
    assert r.status_code == 400
    assert "division by zero" in r.json().get("error", "").lower()


def test_undefined_variable_names_the_variable():
    r = post_json('/api/calc', {"expr": "a + 1"})
    assert r.status_code == 400
    assert "undefined variable" in r.json().get("error", "").lower()
    assert "a" in r.json().get("error", "").lower()


def test_rejects_invalid_vars_payloads():
    r1 = post_json('/api/vars', {"value": 1})
    assert r1.status_code == 400
    r2 = post_json('/api/vars', {"name": "", "value": 1})
    assert r2.status_code == 400
    headers = {"Content-Type": "application/json"}
    raw = json.dumps({"name": "x", "value": float('inf')}, allow_nan=True)
    r3 = requests.post(BASE_URL + '/api/vars', data=raw, headers=headers, timeout=5)
    assert r3.status_code == 400


def test_syntax_error_for_malformed_expressions():
    r = post_json('/api/calc', {"expr": "2 + * 3"})
    assert r.status_code == 400
    assert "syntax error" in r.json().get("error", "").lower()


def test_whitespace_and_floats():
    r = post_json('/api/calc', {"expr": " 1.5  * ( 2 + 0.5 ) "})
    assert r.status_code == 200
    assert r.json()["result"] == 1.5 * 2.5
