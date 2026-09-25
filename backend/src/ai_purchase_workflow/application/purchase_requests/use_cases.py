from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.dto import (
    CreatePurchaseRequestCommand,
    PurchaseRequestView,
)
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.domain.purchase_requests import Money, PurchaseItem, PurchaseRequest, RequestStatus


class PurchaseRequestNotFoundError(LookupError):
    def __init__(self, request_id: UUID) -> None:
        super().__init__(f"Purchase request {request_id} was not found.")


class CreatePurchaseRequest:
    def __init__(self, repository: PurchaseRequestRepository) -> None:
        self._repository = repository

    async def execute(self, command: CreatePurchaseRequestCommand) -> PurchaseRequestView:
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
        await self._repository.add(request)
        return PurchaseRequestView.from_domain(request)


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

    async def execute(self, status: RequestStatus | None = None) -> tuple[PurchaseRequestView, ...]:
        requests = await self._repository.list(status=status)
        return tuple(PurchaseRequestView.from_domain(request) for request in requests)
