from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.domain.purchase_requests import PurchaseRequest, RequestStatus


@dataclass(frozen=True, slots=True)
class PurchaseRequestPageResult:
    items: tuple[PurchaseRequest, ...]
    total: int


class PurchaseRequestRepository(Protocol):
    async def add(self, request: PurchaseRequest) -> None: ...
    async def save(self, request: PurchaseRequest) -> None: ...
    async def get(self, request_id: UUID) -> PurchaseRequest | None: ...
    async def get_for_update(self, request_id: UUID) -> PurchaseRequest | None: ...
    async def list_page(
        self,
        *,
        status: RequestStatus | None,
        limit: int,
        offset: int,
        descending: bool,
    ) -> PurchaseRequestPageResult: ...
