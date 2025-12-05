import json
import math
import pytest
import requests
from fractions import Fraction
import numpy as np

BASE = "http://localhost:3000"

def test_matrix_operations_addition():
    """Test matrix addition with valid inputs"""
    payload = {
        "matrix1": [[1, 2], [3, 4]],
        "matrix2": [[4, 3], [2, 1]],
        "operation": "add"
    }
    r = requests.post(f"{BASE}/adv/matrix_operations", json=payload, timeout=5)
    assert r.status_code == 200
    assert r.json() == {"result": [[5, 5], [5, 5]]}

def test_matrix_operations_invalid_dimensions():
    """Test matrix multiplication with incompatible dimensions"""
    payload = {
        "matrix1": [[1, 2, 3], [4, 5, 6]],
        "matrix2": [[1, 2], [3, 4]],
        "operation": "multiply"
    }
    r = requests.post(f"{BASE}/adv/matrix_operations", json=payload, timeout=5)
    assert r.status_code == 400
    assert "error" in r.json()

def test_continued_fraction_square_root():
    """Test continued fraction for square root of non-square number"""
    r = requests.get(f"{BASE}/adv/continued_fraction?n=13")
    assert r.status_code == 200
    data = r.json()
    assert "period" in data
    # The continued fraction representation of sqrt(13) is [3; 1,1,1,1,6,1,1,1,1,6,...]
    assert data["period"][0] == 3  # Integer part
    assert 6 in data["period"][1:]  # Should contain 6 in the repeating part

def test_diophantine_solution():
    """Test Diophantine equation solver with solvable equation"""
    r = requests.get(f"{BASE}/adv/diophantine?a=3&b=5&c=8")
    assert r.status_code == 200
    data = r.json()
    assert "solution" in data
    x = data["solution"]["x"]
    y = data["solution"]["y"]
    assert 3*x + 5*y == 8

def test_diophantine_no_solution():
    """Test Diophantine equation with no solution"""
    r = requests.get(f"{BASE}/adv/diophantine?a=2&b=4&c=5")
    assert r.status_code == 400
    assert "error" in r.json()

def test_matrix_determinant():
    """Test matrix determinant calculation"""
    payload = {
        "matrix1": [[4, 7], [2, 6]],
        "operation": "determinant"
    }
    r = requests.post(f"{BASE}/adv/matrix_operations", json=payload, timeout=5)
    assert r.status_code == 200
    assert r.json() == {"result": 10}  # 4*6 - 7*2 = 10

# Additional edge case tests
def test_continued_fraction_perfect_square():
    """Test continued fraction for perfect square"""
    r = requests.get(f"{BASE}/adv/continued_fraction?n=16")
    assert r.status_code == 200
    assert r.json() == {"period": [4]}

def test_matrix_operations_large_matrices():
    """Test matrix operations with larger matrices"""
    # This test will be skipped in initial runs as it's more of a performance test
    size = 20
    matrix = [[(i + j) % 10 for j in range(size)] for i in range(size)]
    payload = {
        "matrix1": matrix,
        "matrix2": [[1 if i == j else 0 for j in range(size)] for i in range(size)],
        "operation": "multiply"
    }
    r = requests.post(f"{BASE}/adv/matrix_operations", json=payload, timeout=10)
    assert r.status_code == 200
    result = r.json()["result"]
    assert len(result) == size
    assert len(result[0]) == size

# Error case tests
def test_invalid_matrix():
    """Test with invalid matrix input"""
    payload = {
        "matrix1": [[1, 2], [3]],  # Jagged array
        "operation": "determinant"
    }
    r = requests.post(f"{BASE}/adv/matrix_operations", json=payload, timeout=5)
    assert r.status_code == 400

# This test will be skipped initially as it's more complex
def test_diophantine_negative_coefficients():
    """Test Diophantine equation with negative coefficients"""
    r = requests.get(f"{BASE}/adv/diophantine?a=-3&b=5&c=1")
    assert r.status_code == 200
    data = r.json()
    x = data["solution"]["x"]
    y = data["solution"]["y"]
    assert -3*x + 5*y == 1
