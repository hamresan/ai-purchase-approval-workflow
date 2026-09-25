from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.dto import PurchaseRequestView
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
    SubmitOrder,
)
from ai_purchase_workflow.application.purchase_requests.use_cases import (
    PurchaseRequestNotFoundError,
)
from ai_purchase_workflow.domain.purchase_requests import AuditEntry, PurchaseItem, RequestStatus


class PreparePurchaseRequest:
    def __init__(
        self,
        repository: PurchaseRequestRepository,
        find_vendor: FindVendor,
        create_draft_order: CreateDraftOrder,
        check_budget: CheckBudget,
    ) -> None:
        self._repository = repository
        self._find_vendor = find_vendor
        self._create_draft_order = create_draft_order
        self._check_budget = check_budget

    async def execute(self, request_id: UUID) -> PurchaseRequestView:
        request = await self._repository.get(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)

        trusted_items: list[PurchaseItem] = []
        for item in request.items:
            trusted_items.append(await self._find_vendor.execute(item))
        resolved_items = tuple(trusted_items)
        draft = self._create_draft_order.execute(request, resolved_items)
        await self._check_budget.execute(request.requester_name, draft.total)
        request.draft_order = draft
        request.audit_entries = (
            *request.audit_entries,
            AuditEntry.create(
                request.id,
                "purchase_request_prepared",
                "Trusted purchase data validated and draft order created.",
            ),
        )
        request.transition_to(RequestStatus.PENDING_APPROVAL)
        await self._repository.save(request)
        return PurchaseRequestView.from_domain(request)


class SubmitPurchaseRequest:
    def __init__(self, repository: PurchaseRequestRepository, submit_order: SubmitOrder) -> None:
        self._repository = repository
        self._submit_order = submit_order

    async def execute(self, request_id: UUID) -> PurchaseRequestView:
        request = await self._repository.get(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)

        await self._submit_order.execute(request)
        request.transition_to(RequestStatus.SUBMITTED)
        await self._repository.save(request)
        return PurchaseRequestView.from_domain(request)
