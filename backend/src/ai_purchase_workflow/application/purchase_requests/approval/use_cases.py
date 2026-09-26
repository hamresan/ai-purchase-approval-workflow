from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.approval.contracts import (
    PurchaseRequestWorkflowGateway,
)
from ai_purchase_workflow.application.purchase_requests.approval.dto import EditPurchaseItem
from ai_purchase_workflow.application.purchase_requests.dto import PurchaseRequestView
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.application.purchase_requests.trusted_tools import (
    CheckBudget,
    CreateDraftOrder,
    FindVendor,
)
from ai_purchase_workflow.application.purchase_requests.use_cases import (
    PurchaseRequestNotFoundError,
)
from ai_purchase_workflow.domain.purchase_requests import (
    ApprovalDecision,
    ApprovalOutcome,
    AuditEntry,
    DomainValidationError,
    RequestStatus,
)


class PurchaseRequestApprovalError(DomainValidationError):
    """Raised when an approval action is invalid for the current request state."""


class ApprovePurchaseRequest:
    def __init__(
        self,
        repository: PurchaseRequestRepository,
        workflow: PurchaseRequestWorkflowGateway,
    ) -> None:
        self._repository = repository
        self._workflow = workflow

    async def execute(
        self,
        request_id: UUID,
        *,
        decided_by: str,
        reason: str | None = None,
    ) -> PurchaseRequestView:
        request = await self._repository.get_for_update(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)
        if request.status is RequestStatus.SUBMITTED:
            return PurchaseRequestView.from_domain(request)
        if request.status is RequestStatus.APPROVED:
            return PurchaseRequestView.from_domain(request)
        if request.status is not RequestStatus.PENDING_APPROVAL:
            raise PurchaseRequestApprovalError("Only pending requests can be approved.")

        request.approval_decision = ApprovalDecision.create(
            request.id,
            ApprovalOutcome.APPROVED,
            decided_by,
            reason,
        )
        request.audit_entries = (
            *request.audit_entries,
            AuditEntry.create(
                request.id,
                "approval_approved",
                "Purchase request approved by a human reviewer.",
            ),
        )
        request.transition_to(RequestStatus.APPROVED)
        await self._repository.save(request)
        await self._workflow.resume_approved(request.id)
        refreshed = await self._repository.get(request.id)
        return PurchaseRequestView.from_domain(refreshed or request)


class RejectPurchaseRequest:
    def __init__(
        self,
        repository: PurchaseRequestRepository,
        workflow: PurchaseRequestWorkflowGateway,
    ) -> None:
        self._repository = repository
        self._workflow = workflow

    async def execute(
        self,
        request_id: UUID,
        *,
        decided_by: str,
        reason: str | None = None,
    ) -> PurchaseRequestView:
        request = await self._repository.get_for_update(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)
        if request.status is RequestStatus.REJECTED:
            return PurchaseRequestView.from_domain(request)
        if request.status is not RequestStatus.PENDING_APPROVAL:
            raise PurchaseRequestApprovalError("Only pending requests can be rejected.")

        request.approval_decision = ApprovalDecision.create(
            request.id,
            ApprovalOutcome.REJECTED,
            decided_by,
            reason,
        )
        request.audit_entries = (
            *request.audit_entries,
            AuditEntry.create(
                request.id,
                "approval_rejected",
                "Purchase request rejected by a human reviewer.",
            ),
        )
        request.transition_to(RequestStatus.REJECTED)
        await self._repository.save(request)
        await self._workflow.resume_rejected(request.id)
        return PurchaseRequestView.from_domain(request)


class EditPurchaseRequest:
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

    async def execute(
        self,
        request_id: UUID,
        *,
        items: tuple[EditPurchaseItem, ...],
        decided_by: str,
    ) -> PurchaseRequestView:
        request = await self._repository.get_for_update(request_id)
        if request is None:
            raise PurchaseRequestNotFoundError(request_id)
        if request.status is not RequestStatus.PENDING_APPROVAL:
            raise PurchaseRequestApprovalError("Only pending requests can be edited.")
        if not items:
            raise PurchaseRequestApprovalError("An edited request must contain at least one item.")

        resolved_items = tuple(
            [await self._find_vendor.resolve(item.description, item.quantity) for item in items]
        )
        revised_draft = self._create_draft_order.execute(request, resolved_items)
        await self._check_budget.execute(request.requester_name, revised_draft.total)

        request.items = resolved_items
        request.draft_order = revised_draft
        request.audit_entries = (
            *request.audit_entries,
            AuditEntry.create(
                request.id,
                "approval_edited",
                f"Purchase request edited by {decided_by}, "
                "revalidated, and returned to approval review.",
            ),
        )
        await self._repository.save(request)
        return PurchaseRequestView.from_domain(request)
