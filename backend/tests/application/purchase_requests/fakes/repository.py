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
        requester_user_id: UUID | None = None,
    ) -> PurchaseRequestPageResult:
        values = tuple(
            sorted(
                self.requests.values(),
                key=lambda request: (request.created_at, request.id),
                reverse=descending,
            )
        )
        filtered = tuple(
            request
            for request in values
            if (status is None or request.status is status)
            and (requester_user_id is None or request.requester_user_id == requester_user_id)
        )
        return PurchaseRequestPageResult(
            items=filtered[offset : offset + limit],
            total=len(filtered),
        )
