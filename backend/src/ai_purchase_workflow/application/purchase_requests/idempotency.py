from typing import Protocol

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest


class PurchaseRequestIdempotencyStore(Protocol):
    async def get(self, key: str) -> PurchaseRequest | None: ...
    async def bind(self, key: str, request: PurchaseRequest) -> PurchaseRequest: ...
