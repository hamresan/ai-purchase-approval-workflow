from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.repository import (
    PurchaseRequestPageResult,
    PurchaseRequestRepository,
)
from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus


class InMemoryPurchaseRequestRepository(PurchaseRequestRepository):
    def __init__(self) -> None:
        self.requests: dict[UUID, PurchaseRequest] = {}

    async def add(self, request: PurchaseRequest) -> None:
        self.requests[request.id] = request

    async def save(self, request: PurchaseRequest) -> None:
        self.requests[request.id] = request

    async def get(self, request_id: UUID) -> PurchaseRequest | None:
        return self.requests.get(request_id)

    async def get_for_update(self, request_id: UUID) -> PurchaseRequest | None:
        return self.requests.get(request_id)

    async def list_page(
        self,
        *,
        status: RequestStatus | None,
        limit: int,
        offset: int,
        descending: bool,
    ) -> PurchaseRequestPageResult:
        values = tuple(
            sorted(
                self.requests.values(),
                key=lambda request: (request.created_at, request.id),
                reverse=descending,
            )
        )
        filtered = values if status is None else tuple(
            request for request in values if request.status is status
        )
        return PurchaseRequestPageResult(
            items=filtered[offset : offset + limit],
            total=len(filtered),
        )
