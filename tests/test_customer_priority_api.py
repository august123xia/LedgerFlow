import pytest

import app_sqlite
from python.aging_report import build_aging_reports


@pytest.fixture
def client(tmp_path, monkeypatch):
    csv_path = tmp_path / "invoices.csv"
    csv_path.write_text(
        "customer,invoice_date,due_date,amount,status\n"
        "Alpha,2026-08-01,2026-09-01,2500,unpaid\n"
        "Alpha,2026-08-01,2026-09-02,2500,unpaid\n"
        "Beta,2026-08-01,2026-09-01,3000,unpaid\n"
        "Gamma,2026-08-01,2026-09-01,2999,unpaid\n"
        "PaidCo,2026-08-01,2026-09-01,9000,paid\n"
        "FutureCo,2026-08-01,2026-10-01,9000,unpaid\n"
        "DueTodayCo,2026-08-01,2026-09-16,9000,unpaid\n"
    )

    def build_from_fixture(report_date):
        return build_aging_reports(report_date, input_path=csv_path)

    monkeypatch.setattr(app_sqlite, "build_aging_reports", build_from_fixture)
    return app_sqlite.app.test_client()


def test_customer_totals_priorities_and_exclusions(client):
    response = client.get(
        "/reports/customer-priority?report_date=2026-09-16"
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["report_date"] == "2026-09-16"
    assert result["customer_count"] == 3
    assert result["customers"] == [
        {"customer": "Alpha", "total_overdue": 5000, "priority": "High"},
        {"customer": "Beta", "total_overdue": 3000, "priority": "Medium"},
        {"customer": "Gamma", "total_overdue": 2999, "priority": "Low"},
    ]


def test_report_date_changes_customer_list(client):
    response = client.get(
        "/reports/customer-priority?report_date=2026-09-17"
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["customer_count"] == 4
    assert result["customers"][0] == {
        "customer": "DueTodayCo",
        "total_overdue": 9000,
        "priority": "High",
    }


def test_no_overdue_customers(client):
    response = client.get(
        "/reports/customer-priority?report_date=2026-08-01"
    )

    assert response.status_code == 200
    result = response.get_json()
    assert result["customer_count"] == 0
    assert result["customers"] == []


@pytest.mark.parametrize(
    "query",
    [
        "",
        "?report_date=invalid",
        "?report_date=2026-02-30",
        "?report_date=20260916",
    ],
)
def test_invalid_report_date(client, query):
    response = client.get("/reports/customer-priority" + query)
    assert response.status_code == 400
    assert "error" in response.get_json()
