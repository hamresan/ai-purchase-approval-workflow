from uuid import UUID

import pytest

from ai_purchase_workflow.application.purchase_requests.repository import (
    PurchaseRequestRepository,
)
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus


class InMemoryPurchaseRequestRepository(PurchaseRequestRepository):
    def __init__(self) -> None:
        self.requests: dict[UUID, PurchaseRequest] = {}

    async def add(self, request: PurchaseRequest) -> None:
        self.requests[request.id] = request

    async def get(self, request_id: UUID) -> PurchaseRequest | None:
        return self.requests.get(request_id)

    async def list(
        self,
        status: RequestStatus | None = None,
    ) -> tuple[PurchaseRequest, ...]:
        values = tuple(sorted(self.requests.values(), key=lambda request: request.created_at))
        if status is None:
            return values
        return tuple(request for request in values if request.status is status)


@pytest.fixture
def repository() -> PurchaseRequestRepository:
    return InMemoryPurchaseRequestRepository()
