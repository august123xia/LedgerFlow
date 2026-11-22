from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from openai import APIError

import app_sqlite
import payment_analysis
from payment_analysis import Analysis, PossibleCause


@pytest.fixture
def client():
    return app_sqlite.app.test_client()


def payload():
    return {
        "invoice_amount": 5000,
        "received_amount": 4992,
        "customer_claim": "Customer claims full payment",
    }


def test_success_keeps_bank_fee_unverified(client, monkeypatch):
    llm = Mock()
    llm.responses.parse.return_value = SimpleNamespace(
        output_parsed=Analysis(
            possible_causes=[
                PossibleCause(
                    reason="A bank fee may explain the shortfall.",
                    verification_needed="Check the bank fee breakdown.",
                )
            ],
            next_steps=["Request remittance advice."],
        )
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    monkeypatch.setattr(payment_analysis, "OpenAI", Mock(return_value=llm))

    response = client.post("/payments/analyze", json=payload())

    assert response.status_code == 200
    result = response.get_json()
    assert result["discrepancy_amount"] == "8"
    assert result["analysis_status"] == "unverified"
    assert result["possible_causes"][0]["status"] == "unverified"
    llm.responses.parse.assert_called_once()


@pytest.mark.parametrize("body", [None, [], {}, {"invoice_amount": -1}])
def test_invalid_input(client, body):
    response = client.post("/payments/analyze", json=body)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_malformed_json(client):
    response = client.post(
        "/payments/analyze",
        data="{broken",
        content_type="application/json",
    )
    assert response.status_code == 400


def test_missing_key(client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post("/payments/analyze", json=payload())
    assert response.status_code == 503


def test_provider_failure_does_not_expose_details(client, monkeypatch):
    analyze = Mock(
        side_effect=APIError(
            "private-provider-details", request=Mock(), body=None
        )
    )
    monkeypatch.setattr(app_sqlite, "analyze_payment", analyze)

    response = client.post("/payments/analyze", json=payload())

    assert response.status_code == 502
    assert "private-provider-details" not in response.get_data(as_text=True)
