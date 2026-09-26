from ai_purchase_workflow.application.purchase_requests.idempotency import (
    IdempotentPurchaseRequestCreator,
)
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest


class InMemoryIdempotentPurchaseRequestCreator(IdempotentPurchaseRequestCreator):
    def __init__(self) -> None:
        self.requests: dict[str, PurchaseRequest] = {}

    async def create(self, key: str, request: PurchaseRequest) -> PurchaseRequest:
        existing = self.requests.get(key)
        if existing is not None:
            return existing
        self.requests[key] = request
        return request
