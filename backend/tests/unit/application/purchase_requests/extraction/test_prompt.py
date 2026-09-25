from ai_purchase_workflow.application.purchase_requests.extraction import (
    PurchaseRequestPromptBuilder,
)
from ai_purchase_workflow.application.purchase_requests.extraction.prompt import (
    PromptTemplateReader,
)


class FakePromptTemplateReader(PromptTemplateReader):
    def read(self, name: str, version: str) -> str:
        assert name == "purchase_request_extraction"
        assert version == "v1"
        return "Schema {schema_version}. Do not invent price, vendor, budget."


def test_build_normalizes_input_and_renders_versioned_template() -> None:
    request = PurchaseRequestPromptBuilder(FakePromptTemplateReader()).build(
        "  Buy two laptop stands  "
    )

    assert request.user_prompt == "Buy two laptop stands"
    assert request.system_prompt == "Schema 1.0. Do not invent price, vendor, budget."


def test_build_rejects_empty_text() -> None:
    try:
        PurchaseRequestPromptBuilder(FakePromptTemplateReader()).build("   ")
    except ValueError as error:
        assert str(error) == "Purchase request text must not be empty."
    else:
        raise AssertionError("Expected empty purchase request text to be rejected.")
