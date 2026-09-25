from ai_purchase_workflow.application.purchase_requests.extraction import (
    PurchaseRequestPromptBuilder,
)
from tests.application.purchase_requests.fakes.prompt import FakePromptTemplateReader


def test_build_normalizes_input_and_renders_versioned_template() -> None:
    reader = FakePromptTemplateReader("Schema {schema_version}. Do not invent price.")
    request = PurchaseRequestPromptBuilder(reader).build("  Buy two laptop stands  ")

    assert request.user_prompt == "Buy two laptop stands"
    assert request.system_prompt == "Schema 1.0. Do not invent price."
    assert reader.requests == [("purchase_request_extraction", "v1")]


def test_build_rejects_empty_text() -> None:
    try:
        PurchaseRequestPromptBuilder(FakePromptTemplateReader()).build("   ")
    except ValueError as error:
        assert str(error) == "Purchase request text must not be empty."
    else:
        raise AssertionError("Expected empty purchase request text to be rejected.")
