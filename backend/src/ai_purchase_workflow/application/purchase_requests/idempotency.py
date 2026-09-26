from typing import Protocol

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest


class IdempotentPurchaseRequestCreator(Protocol):
    async def create(self, key: str, request: PurchaseRequest) -> PurchaseRequest: ...
