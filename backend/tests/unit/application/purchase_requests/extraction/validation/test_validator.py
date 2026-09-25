import pytest

from ai_purchase_workflow.application.purchase_requests.extraction import (
    AmbiguousExtractionError,
    ExtractedPurchaseItem,
    ExtractedPurchaseRequest,
    ExtractedRequestValidator,
    MalformedModelOutputError,
)


def test_validate_accepts_complete_extraction() -> None:
    extracted = ExtractedPurchaseRequest(
        schema_version="1.0",
        requester_name="Dana",
        items=(ExtractedPurchaseItem("Laptop stand", 2),),
    )

    ExtractedRequestValidator().validate(extracted)


def test_validate_routes_ambiguous_extraction_to_human_review() -> None:
    extracted = ExtractedPurchaseRequest(
        schema_version="1.0",
        requester_name=None,
        items=(),
        needs_human_review=True,
        review_reason="Quantity is ambiguous.",
    )

    with pytest.raises(AmbiguousExtractionError, match="Quantity is ambiguous"):
        ExtractedRequestValidator().validate(extracted)


@pytest.mark.parametrize(
    "extracted",
    [
        ExtractedPurchaseRequest("2.0", None, (ExtractedPurchaseItem("Stand", 1),)),
        ExtractedPurchaseRequest("1.0", None, ()),
        ExtractedPurchaseRequest("1.0", None, (ExtractedPurchaseItem("", 1),)),
        ExtractedPurchaseRequest("1.0", None, (ExtractedPurchaseItem("Stand", 0),)),
    ],
)
def test_validate_rejects_invalid_extraction(extracted: ExtractedPurchaseRequest) -> None:
    with pytest.raises(MalformedModelOutputError):
        ExtractedRequestValidator().validate(extracted)
