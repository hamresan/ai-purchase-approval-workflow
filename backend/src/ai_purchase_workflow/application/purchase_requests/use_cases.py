from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.dto import (
    CreatePurchaseRequestCommand,
    PurchaseRequestListQuery,
    PurchaseRequestPage,
    PurchaseRequestView,
)
from ai_purchase_workflow.application.purchase_requests.idempotency import IdempotentPurchaseRequestCreator
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.domain.purchase_requests import Money, PurchaseItem, PurchaseRequest


class PurchaseRequestNotFoundError(LookupError):
    def __init__(self, request_id: UUID) -> None:
        super().__init__(f"Purchase request {request_id} was not found.")


class CreatePurchaseRequest:
    def __init__(
        self,
        repository: PurchaseRequestRepository,
        idempotent_creator: IdempotentPurchaseRequestCreator,
    ) -> None:
        self._repository = repository
        self._idempotent_creator = idempotent_creator

    async def execute(
        self,
        command: CreatePurchaseRequestCommand,
        idempotency_key: str | None = None,
    ) -> PurchaseRequestView:
        items = tuple(
            PurchaseItem(
                description=item.description,
                quantity=item.quantity,
                unit_price=Money(item.unit_price_amount, item.currency),
                vendor=item.vendor,
            )
            for item in command.items
        )
        request = PurchaseRequest.create(items=items, requester_name=command.requester_name)
        if idempotency_key is None:
            await self._repository.add(request)
            persisted = request
        else:
            persisted = await self._idempotent_creator.create(idempotency_key, request)
        return PurchaseRequestView.from_domain(persisted)


class GetPurchaseRequest:
    def __init__(self, repository: PurchaseRequestRepository) -> None:
        self._repository = repository

    async def execute(self, request_id: UUID) -> PurchaseRequestView:
        request = await self._repository.get(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)
        return PurchaseRequestView.from_domain(request)


class ListPurchaseRequests:
    def __init__(self, repository: PurchaseRequestRepository) -> None:
        self._repository = repository

    async def execute(self, query: PurchaseRequestListQuery) -> PurchaseRequestPage:
        page = await self._repository.list_page(
            status=query.status,
            limit=query.limit,
            offset=query.offset,
            descending=query.descending,
        )
        return PurchaseRequestPage(
            items=tuple(PurchaseRequestView.from_domain(request) for request in page.items),
            total=page.total,
            limit=query.limit,
            offset=query.offset,
        )
