from typing import Protocol

from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    EXTRACTED_REQUEST_SCHEMA_VERSION,
    ExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    AmbiguousExtractionError,
    MalformedModelOutputError,
)


class ExtractedRequestValidationRule(Protocol):
    def validate(self, extracted: ExtractedPurchaseRequest) -> None: ...


class SchemaVersionRule(ExtractedRequestValidationRule):
    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        if extracted.schema_version != EXTRACTED_REQUEST_SCHEMA_VERSION:
            raise MalformedModelOutputError("Unsupported extraction schema version.")


class HumanReviewRule(ExtractedRequestValidationRule):
    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        if extracted.needs_human_review:
            raise AmbiguousExtractionError(
                extracted.review_reason or "Purchase request requires human review."
            )


class ItemsPresentRule(ExtractedRequestValidationRule):
    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        if not extracted.items:
            raise MalformedModelOutputError("Extracted purchase request has no items.")


class ItemDescriptionRule(ExtractedRequestValidationRule):
    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        if any(not item.description.strip() for item in extracted.items):
            raise MalformedModelOutputError("Extracted item description must not be empty.")


class ItemQuantityRule(ExtractedRequestValidationRule):
    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        if any(item.quantity <= 0 for item in extracted.items):
            raise MalformedModelOutputError("Extracted item quantity must be positive.")
