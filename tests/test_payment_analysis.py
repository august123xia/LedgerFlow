import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from payment_analysis import Analysis, PossibleCause, analyze_payment


def make_client():
    client = Mock()
    client.responses.parse.return_value = SimpleNamespace(
        output_parsed=Analysis(
            possible_causes=[
                PossibleCause(
                    reason="A bank fee may explain the shortfall.",
                    verification_needed="Obtain the bank transfer fee breakdown.",
                )
            ],
            next_steps=["Request remittance advice and compare bank records."],
        )
    )
    return client


def test_shortfall_and_bank_fee_remain_unverified():
    client = make_client()

    result = analyze_payment(
        5000, 4992, "Customer claims full payment", client=client
    )

    assert result["discrepancy_amount"] == "8"
    assert result["analysis_status"] == "unverified"
    assert result["possible_causes"][0]["status"] == "unverified"
    assert result["possible_causes"][0]["verification_needed"]
    client.responses.parse.assert_called_once()
    facts = json.loads(client.responses.parse.call_args.kwargs["input"])
    assert facts["discrepancy_amount"] == "8"


def test_decimal_amounts_are_exact():
    result = analyze_payment(
        "100.10", "100.02", "Paid in full", client=make_client()
    )
    assert result["discrepancy_amount"] == "0.08"


@pytest.mark.parametrize(
    "invoice,received,claim",
    [
        (True, 4992, "Paid"),
        (5000, -1, "Paid"),
        (5000, float("nan"), "Paid"),
        (5000, float("inf"), "Paid"),
        ("invalid", 4992, "Paid"),
        ("10.001", 9, "Paid"),
        (0, 0, "Paid"),
        (5000, 4992, ""),
        (5000, 4992, None),
    ],
)
def test_invalid_input_is_rejected_before_llm_call(invoice, received, claim):
    client = make_client()
    with pytest.raises(ValueError):
        analyze_payment(invoice, received, claim, client=client)
    client.responses.parse.assert_not_called()


def test_missing_key_has_clear_error(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        analyze_payment(5000, 4992, "Paid in full")


def test_unusable_model_response_is_not_reported_as_success():
    client = make_client()
    client.responses.parse.return_value.output_parsed = None
    with pytest.raises(RuntimeError, match="usable analysis"):
        analyze_payment(5000, 4992, "Paid in full", client=client)
