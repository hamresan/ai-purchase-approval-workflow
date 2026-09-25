from typing import cast

from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseItem,
)
from ai_purchase_workflow.application.purchase_requests.extraction.errors import (
    MalformedModelOutputError,
)

StructuredObject = dict[str, object]


def as_structured_object(value: object, error_message: str) -> StructuredObject:
    if not isinstance(value, dict):
        raise MalformedModelOutputError(error_message)
    return cast(StructuredObject, value)


def required_string(value: StructuredObject, key: str) -> str:
    field = value.get(key)
    if not isinstance(field, str) or not field.strip():
        raise MalformedModelOutputError(f"Model output field '{key}' must be text.")
    return field.strip()


def optional_string(value: StructuredObject, key: str) -> str | None:
    field = value.get(key)
    if field is None:
        return None
    if not isinstance(field, str) or not field.strip():
        raise MalformedModelOutputError(f"Model output field '{key}' must be text or null.")
    return field.strip()


def optional_bool(value: StructuredObject, key: str) -> bool:
    field = value.get(key, False)
    if not isinstance(field, bool):
        raise MalformedModelOutputError(f"Model output field '{key}' must be boolean.")
    return field


def map_purchase_item(value: object) -> ExtractedPurchaseItem:
    item = as_structured_object(value, "Each extracted item must be an object.")
    quantity = item.get("quantity")
    if not isinstance(quantity, int) or isinstance(quantity, bool):
        raise MalformedModelOutputError("Extracted item quantity must be an integer.")
    return ExtractedPurchaseItem(
        description=required_string(item, "description"),
        quantity=quantity,
    )
