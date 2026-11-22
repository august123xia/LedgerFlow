import pytest

import app_sqlite
from python import soa_generator


@pytest.fixture
def soa_data(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    files = {
        "soa_undisputed_invoices.csv": (
            "invoice_no,due_date,amount\n"
            "INV001,2026-08-01,1200\n"
            "INV002,2026-08-15,800\n"
        ),
        "soa_disputed_invoices.csv": (
            "invoice_no,due_date,amount,reason\n"
            "INV003,2026-08-10,900,Under review\n"
        ),
        "soa_unused_credits.csv": (
            "credit_no,amount\nCN001,300\n"
        ),
        "soa_unallocated_payments.csv": (
            "payment_ref,payment_date,amount\n"
            "PAY001,2026-08-20,500\n"
        ),
    }
    for name, contents in files.items():
        (data_dir / name).write_text(contents)

    output_dir = tmp_path / "outputs"
    monkeypatch.setattr(soa_generator, "DATA_DIR", data_dir)
    monkeypatch.setattr(soa_generator, "OUTPUT_DIR", output_dir)
    return data_dir, output_dir


def test_soa_excludes_disputes_and_deducts_credits_and_payments(soa_data):
    result = soa_generator.build_soa()

    assert result["total_undisputed"] == 2000
    assert result["total_disputed"] == 900
    assert result["total_unused_credits"] == 300
    assert result["total_unallocated_payments"] == 500
    assert result["payment_request"] == 1200


def test_disputed_invoice_is_visible_in_statement(soa_data):
    result = soa_generator.build_soa()

    assert "INV003" in result["statement_text"]
    assert "Under review" in result["statement_text"]
    assert "$1,200.00" in result["statement_text"]


def test_soa_api_returns_statement_without_writing_files(soa_data):
    _, output_dir = soa_data
    with app_sqlite.app.test_client() as client:
        response = client.get("/reports/soa")

    assert response.status_code == 200
    result = response.get_json()
    assert result["scope"] == "single_customer_demo"
    assert result["customer"] == "Customer A"
    assert result["payment_request"] == 1200
    assert result["statement_text"]
    assert not output_dir.exists()


def test_empty_soa_has_zero_payment_request(soa_data):
    data_dir, _ = soa_data
    for path in data_dir.glob("*.csv"):
        header = path.read_text().splitlines()[0]
        path.write_text(header + "\n")

    result = soa_generator.build_soa()

    assert result["total_undisputed"] == 0
    assert result["total_disputed"] == 0
    assert result["total_unused_credits"] == 0
    assert result["total_unallocated_payments"] == 0
    assert result["payment_request"] == 0
