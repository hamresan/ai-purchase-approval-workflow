from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus


class PurchaseRequestRepository(Protocol):
    async def add(self, request: PurchaseRequest) -> None: ...

    async def get(self, request_id: UUID) -> PurchaseRequest | None: ...

    async def list(self, status: RequestStatus | None = None) -> tuple[PurchaseRequest, ...]: ...
