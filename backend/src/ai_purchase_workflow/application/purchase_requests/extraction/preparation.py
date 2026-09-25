from ai_purchase_workflow.application.purchase_requests.dto import PurchaseRequestView
from ai_purchase_workflow.application.purchase_requests.extraction.contracts import (
    ExtractedPurchaseRequest,
)
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
)
from ai_purchase_workflow.domain.purchase_requests import AuditEntry, PurchaseRequest, RequestStatus


class PurchaseRequestPreparationError(Exception):
    """Expected failure while preparing an extracted purchase request."""


class PrepareExtractedPurchaseRequest:
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

    async def execute(self, extracted: ExtractedPurchaseRequest) -> PurchaseRequestView:
        try:
            trusted_items = tuple(
                [
                    await self._find_vendor.resolve(item.description, item.quantity)
                    for item in extracted.items
                ]
            )
            request = PurchaseRequest.create(trusted_items, extracted.requester_name)
            draft = self._create_draft_order.execute(request, trusted_items)
            await self._check_budget.execute(request.requester_name, draft.total)
        except Exception as error:
            raise PurchaseRequestPreparationError(str(error)) from error
        request.draft_order = draft
        request.audit_entries = (
            *request.audit_entries,
            AuditEntry.create(
                request.id,
                "purchase_request_prepared",
                "AI-extracted request validated with trusted data and draft order created.",
            ),
        )
        request.transition_to(RequestStatus.PENDING_APPROVAL)
        await self._repository.add(request)
        return PurchaseRequestView.from_domain(request)
