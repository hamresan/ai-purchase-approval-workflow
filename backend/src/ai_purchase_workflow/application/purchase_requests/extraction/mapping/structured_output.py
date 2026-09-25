from typing import cast

from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseRequest,
    ModelResponse,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    MalformedModelOutputError,
)

from .structured_values import (
    as_structured_object,
    map_purchase_item,
    optional_bool,
    optional_string,
    required_string,
)

_ALLOWED_OUTPUT_FIELDS = frozenset(
    {"schema_version", "requester_name", "items", "needs_human_review", "review_reason"}
)


class StructuredOutputMapper:
    def map(self, response: ModelResponse) -> ExtractedPurchaseRequest:
        content = as_structured_object(
            response.content,
            "Model output must be a structured object.",
        )
        unexpected_fields = set(content) - _ALLOWED_OUTPUT_FIELDS
        if unexpected_fields:
            fields = ", ".join(sorted(unexpected_fields))
            raise MalformedModelOutputError(f"Model output contains forbidden fields: {fields}.")

        items_value = content.get("items")
        if not isinstance(items_value, list):
            raise MalformedModelOutputError("Model output items must be a list.")

        raw_items = cast(list[object], items_value)
        return ExtractedPurchaseRequest(
            schema_version=required_string(content, "schema_version"),
            requester_name=optional_string(content, "requester_name"),
            items=tuple(map_purchase_item(item) for item in raw_items),
            needs_human_review=optional_bool(content, "needs_human_review"),
            review_reason=optional_string(content, "review_reason"),
        )
