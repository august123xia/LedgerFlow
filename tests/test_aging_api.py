import pytest

import app_sqlite
from python.aging_report import build_aging_reports


@pytest.fixture
def client(tmp_path, monkeypatch):
    csv_path = tmp_path / "invoices.csv"
    csv_path.write_text(
        "invoice_date,due_date,amount,status\n"
        "2026-08-01,2026-09-15,100,unpaid\n"
        "2026-08-01,2026-09-16,200,unpaid\n"
        "2026-08-01,2026-09-17,300,unpaid\n"
        "2026-08-01,2026-09-01,400,paid\n"
    )

    def build_from_fixture(report_date):
        return build_aging_reports(report_date, input_path=csv_path)

    monkeypatch.setattr(app_sqlite, "build_aging_reports", build_from_fixture)
    return app_sqlite.app.test_client()


def test_aging_summary_excludes_paid_and_not_yet_overdue(client):
    response = client.get("/reports/aging?report_date=2026-09-16")

    assert response.status_code == 200
    result = response.get_json()
    assert result["report_date"] == "2026-09-16"
    assert result["unpaid_invoice_count"] == 3
    assert result["total_unpaid"] == 600
    assert result["overdue_invoice_count"] == 1
    assert result["total_overdue"] == 100
    assert result["overdue_summary_by_bucket"] == [
        {"aging_bucket": "0-30 days", "amount": 100}
    ]


def test_report_date_changes_overdue_results(client):
    response = client.get("/reports/aging?report_date=2026-09-18")
    result = response.get_json()

    assert response.status_code == 200
    assert result["overdue_invoice_count"] == 3
    assert result["total_overdue"] == 600


def test_no_overdue_invoices_returns_empty_summary(client):
    response = client.get("/reports/aging?report_date=2026-09-01")
    result = response.get_json()

    assert response.status_code == 200
    assert result["overdue_invoice_count"] == 0
    assert result["total_overdue"] == 0
    assert result["overdue_summary_by_bucket"] == []


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
    response = client.get("/reports/aging" + query)
    assert response.status_code == 400
    assert "error" in response.get_json()
