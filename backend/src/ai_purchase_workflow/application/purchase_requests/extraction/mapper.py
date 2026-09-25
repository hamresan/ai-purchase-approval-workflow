from collections.abc import Mapping

from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseItem,
    ExtractedPurchaseRequest,
    ModelResponse,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    MalformedModelOutputError,
)

StructuredObject = Mapping[str, object]


class StructuredOutputMapper:
    def map(self, response: ModelResponse) -> ExtractedPurchaseRequest:
        content = self._as_object(response.content, "Model output must be a structured object.")
        items_value = content.get("items")
        if not isinstance(items_value, list):
            raise MalformedModelOutputError("Model output items must be a list.")

        items = tuple(self._map_item(item) for item in items_value)
        return ExtractedPurchaseRequest(
            schema_version=self._required_string(content, "schema_version"),
            requester_name=self._optional_string(content, "requester_name"),
            items=items,
            needs_human_review=self._optional_bool(content, "needs_human_review"),
            review_reason=self._optional_string(content, "review_reason"),
        )

    def _map_item(self, value: object) -> ExtractedPurchaseItem:
        item = self._as_object(value, "Each extracted item must be an object.")
        quantity = item.get("quantity")
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise MalformedModelOutputError("Extracted item quantity must be an integer.")
        return ExtractedPurchaseItem(
            description=self._required_string(item, "description"),
            quantity=quantity,
        )

    @staticmethod
    def _as_object(value: object, error_message: str) -> StructuredObject:
        if not isinstance(value, dict):
            raise MalformedModelOutputError(error_message)
        return {str(key): item for key, item in value.items()}

    @staticmethod
    def _required_string(value: StructuredObject, key: str) -> str:
        field = value.get(key)
        if not isinstance(field, str) or not field.strip():
            raise MalformedModelOutputError(f"Model output field '{key}' must be text.")
        return field.strip()

    @staticmethod
    def _optional_string(value: StructuredObject, key: str) -> str | None:
        field = value.get(key)
        if field is None:
            return None
        if not isinstance(field, str) or not field.strip():
            raise MalformedModelOutputError(f"Model output field '{key}' must be text or null.")
        return field.strip()

    @staticmethod
    def _optional_bool(value: StructuredObject, key: str) -> bool:
        field = value.get(key, False)
        if not isinstance(field, bool):
            raise MalformedModelOutputError(f"Model output field '{key}' must be boolean.")
        return field
