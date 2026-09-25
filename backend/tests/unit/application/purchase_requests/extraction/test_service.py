import pytest

from ai_purchase_workflow.application.purchase_requests.extraction import (
    ExtractPurchaseRequest,
    ExtractedRequestValidator,
    ModelResponse,
    PurchaseRequestPromptBuilder,
    StructuredOutputMapper,
)
from ai_purchase_workflow.infrastructure.models import FakePurchaseRequestModel
from tests.application.purchase_requests.fakes.prompt import FakePromptTemplateReader


def build_extractor(response: ModelResponse) -> ExtractPurchaseRequest:
    return ExtractPurchaseRequest(
        model=FakePurchaseRequestModel(response),
        prompt_builder=PurchaseRequestPromptBuilder(FakePromptTemplateReader()),
        mapper=StructuredOutputMapper(),
        validator=ExtractedRequestValidator(),
    )


@pytest.mark.asyncio
async def test_execute_returns_valid_extraction() -> None:
    extractor = build_extractor(
        ModelResponse(
            {
                "schema_version": "1.0",
                "requester_name": "Dana",
                "items": [{"description": "Laptop stand", "quantity": 2}],
            }
        )
    )

    outcome = await extractor.execute("Buy two laptop stands for Dana")

    assert outcome.needs_human_review is False
    assert outcome.extracted_request is not None
    assert outcome.extracted_request.items[0].quantity == 2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content", "reason"),
    [
        (
            {
                "schema_version": "1.0",
                "items": [],
                "needs_human_review": True,
                "review_reason": "Quantity is ambiguous.",
            },
            "Quantity is ambiguous.",
        ),
        ("malformed", "Model output must be a structured object."),
        (
            {
                "schema_version": "1.0",
                "items": [{"description": "Laptop stand", "quantity": 1}],
                "tool_calls": [{"name": "submit_order"}],
            },
            "forbidden fields: tool_calls",
        ),
    ],
)
async def test_execute_falls_back_to_human_review(content: object, reason: str) -> None:
    outcome = await build_extractor(ModelResponse(content)).execute("request")

    assert outcome.extracted_request is None
    assert outcome.needs_human_review is True
    assert reason in (outcome.review_reason or "")
