from dataclasses import dataclass

EXTRACTED_REQUEST_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class ExtractedPurchaseItem:
    description: str
    quantity: int


@dataclass(frozen=True, slots=True)
class ExtractedPurchaseRequest:
    schema_version: str
    requester_name: str | None
    items: tuple[ExtractedPurchaseItem, ...]
    needs_human_review: bool = False
    review_reason: str | None = None
