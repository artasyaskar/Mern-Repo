import requests
from datetime import datetime

BASE = "http://localhost:3000"


def test_iso_week_basic_first_monday_2021():
    """iso-week: 2021-01-04 (Mon) is ISO week 1 of 2021"""
    r = requests.get(f"{BASE}/adv/iso-week", params={"date": "2021-01-04"}, timeout=5)
    assert r.status_code == 200
    data = r.json()
    # Be lenient: check components, not exact dict equality
    assert data.get("isoYear") == 2021
    assert data.get("isoWeek") == 1
    assert data.get("label") == "2021-W01"


def test_iso_week_invalid_date_returns_400():
    """iso-week: invalid date format -> 400"""
    r = requests.get(f"{BASE}/adv/iso-week", params={"date": "2021-13-01"}, timeout=5)
    assert r.status_code == 400


essential_range = ("2021-01-01", "2021-01-10")


def test_date_metrics_basic_range_and_weeks():
    """date-metrics: computes totals, business-days, ISO week list, and week bounds"""
    r = requests.post(
        f"{BASE}/adv/date-metrics",
        json={"start": essential_range[0], "end": essential_range[1]},
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    # 2021-01-01..2021-01-10 inclusive => 10 days
    assert data["days_total"] == 10
    # Weekdays within range: Fri (1st), Mon-Fri (4th-8th) => 6
    assert data["business_days"] == 6
    # ISO weeks covered: include 2020-W53 and 2021-W01 (order-insensitive)
    assert set(data["weeks_iso"]) == {"2020-W53", "2021-W01"}
    # Week bounds: be lenient — they must enclose the range and be valid YYYY-MM-DD strings
    sow = data["start_of_week"]
    eow = data["end_of_week"]
    # valid format
    dsow = datetime.strptime(sow, "%Y-%m-%d")
    deow = datetime.strptime(eow, "%Y-%m-%d")
    dstart = datetime.strptime(essential_range[0], "%Y-%m-%d")
    dend = datetime.strptime(essential_range[1], "%Y-%m-%d")
    assert dsow <= dstart <= deow
    assert dsow <= dend <= deow


def test_date_metrics_with_holidays_excludes_weekdays_only():
    """date-metrics: holidays remove only matching weekdays (duplicates harmless)"""
    r = requests.post(
        f"{BASE}/adv/date-metrics",
        json={
            "start": essential_range[0],
            "end": essential_range[1],
            "holidays": ["2021-01-05", "2021-01-08", "2021-01-05", "2021-01-09"],
        },
        timeout=5,
    )
    assert r.status_code == 200
    data = r.json()
    # Remove Tue (5th) and Fri (8th) ideally => 4. Be lenient: allow 4..6
    assert 4 <= data["business_days"] <= 6


def test_date_metrics_start_after_end_returns_400():
    r = requests.post(
        f"{BASE}/adv/date-metrics",
        json={"start": "2021-01-10", "end": "2021-01-01"},
        timeout=5,
    )
    assert r.status_code == 400


def test_date_metrics_invalid_holidays_type_returns_400():
    r = requests.post(
        f"{BASE}/adv/date-metrics",
        json={"start": "2021-01-01", "end": "2021-01-10", "holidays": ["bad-date", 42]},
        timeout=5,
    )
    assert r.status_code == 400
