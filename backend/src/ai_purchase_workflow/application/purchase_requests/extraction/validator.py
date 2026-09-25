from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    EXTRACTED_REQUEST_SCHEMA_VERSION,
    ExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    AmbiguousExtractionError,
    MalformedModelOutputError,
)


class ExtractedRequestValidator:
    def validate(self, extracted: ExtractedPurchaseRequest) -> None:
        if extracted.schema_version != EXTRACTED_REQUEST_SCHEMA_VERSION:
            raise MalformedModelOutputError("Unsupported extraction schema version.")
        if extracted.needs_human_review:
            raise AmbiguousExtractionError(
                extracted.review_reason or "Purchase request requires human review."
            )
        if not extracted.items:
            raise MalformedModelOutputError("Extracted purchase request has no items.")
        for item in extracted.items:
            if not item.description.strip():
                raise MalformedModelOutputError("Extracted item description must not be empty.")
            if item.quantity <= 0:
                raise MalformedModelOutputError("Extracted item quantity must be positive.")
