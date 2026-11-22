import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from python.overdue_customer_priority import get_priority


def test_get_priority_high():
    assert get_priority(5000) == "High"


def test_get_priority_medium():
    assert get_priority(3000) == "Medium"


def test_get_priority_low():
    assert get_priority(2999) == "Low"