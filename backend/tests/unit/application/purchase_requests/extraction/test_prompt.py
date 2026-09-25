import pytest

from ai_purchase_workflow.application.purchase_requests.extraction import (
    PurchaseRequestPromptBuilder,
)


def test_build_normalizes_input_and_forbids_untrusted_facts() -> None:
    request = PurchaseRequestPromptBuilder().build("  Buy two laptop stands  ")

    assert request.user_prompt == "Buy two laptop stands"
    assert "Do not invent price, vendor, budget" in request.system_prompt
    assert "schema version 1.0" in request.system_prompt


def test_build_rejects_empty_text() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        PurchaseRequestPromptBuilder().build("   ")
