import requests

BASE = "http://localhost:3000"


def test_iso_week_basic_first_monday_2021():
    """iso-week: 2021-01-04 (Mon) is ISO week 1 of 2021"""
    r = requests.get(f"{BASE}/adv/iso-week", params={"date": "2021-01-04"}, timeout=5)
    assert r.status_code == 200
    data = r.json()
    assert data == {"isoYear": 2021, "isoWeek": 1, "label": "2021-W01"}


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
    # ISO weeks covered: 2020-W53 (Jan 1 2021) and 2021-W01 (week starting Jan 4)
    assert data["weeks_iso"] == ["2020-W53", "2021-W01"]
    # Start belongs to 2020-W53: Monday = 2020-12-28
    assert data["start_of_week"] == "2020-12-28"
    # End belongs to 2021-W01: Sunday = 2021-01-10
    assert data["end_of_week"] == "2021-01-10"


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
    # Remove Tue (5th) and Fri (8th) from 6 weekdays => 4
    assert data["business_days"] == 4


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
