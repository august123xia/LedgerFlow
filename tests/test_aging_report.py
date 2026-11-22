import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from python.aging_report import get_aging_bucket


def test_get_aging_bucket_not_due():
    assert get_aging_bucket(-1) == "Not due"


def test_get_aging_bucket_0_to_30_days():
    assert get_aging_bucket(0) == "0-30 days"
    assert get_aging_bucket(30) == "0-30 days"


def test_get_aging_bucket_31_to_60_days():
    assert get_aging_bucket(31) == "31-60 days"
    assert get_aging_bucket(60) == "31-60 days"


def test_get_aging_bucket_61_to_90_days():
    assert get_aging_bucket(61) == "61-90 days"
    assert get_aging_bucket(90) == "61-90 days"


def test_get_aging_bucket_90_plus_days():
    assert get_aging_bucket(91) == "90+ days"