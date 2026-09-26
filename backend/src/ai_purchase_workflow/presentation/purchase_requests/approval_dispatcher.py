from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.application.purchase_requests import (
    ApprovePurchaseRequest,
    EditPurchaseRequest,
    PurchaseRequestView,
    RejectPurchaseRequest,
)
from ai_purchase_workflow.presentation.purchase_requests.mappers import ApprovalCommandMapper
from ai_purchase_workflow.presentation.purchase_requests.schemas import ApprovalBody


class ApprovalActionHandler(Protocol):
    async def execute(self, request_id: UUID, body: ApprovalBody) -> PurchaseRequestView: ...


class ApproveActionHandler(ApprovalActionHandler):
    def __init__(self, use_case: ApprovePurchaseRequest) -> None:
        self._use_case = use_case

    async def execute(self, request_id: UUID, body: ApprovalBody) -> PurchaseRequestView:
        return await self._use_case.execute(
            request_id,
            decided_by=body.decided_by,
            reason=body.reason,
        )


class RejectActionHandler(ApprovalActionHandler):
    def __init__(self, use_case: RejectPurchaseRequest) -> None:
        self._use_case = use_case

    async def execute(self, request_id: UUID, body: ApprovalBody) -> PurchaseRequestView:
        return await self._use_case.execute(
            request_id,
            decided_by=body.decided_by,
            reason=body.reason,
        )


class EditActionHandler(ApprovalActionHandler):
    def __init__(self, use_case: EditPurchaseRequest) -> None:
        self._use_case = use_case

    async def execute(self, request_id: UUID, body: ApprovalBody) -> PurchaseRequestView:
        return await self._use_case.execute(
            request_id,
            items=ApprovalCommandMapper.edit_items(body),
            decided_by=body.decided_by,
        )


class ApprovalActionDispatcher:
    def __init__(
        self,
        approve: ApproveActionHandler,
        reject: RejectActionHandler,
        edit: EditActionHandler,
    ) -> None:
        self._handlers: dict[str, ApprovalActionHandler] = {
            "approve": approve,
            "reject": reject,
            "edit": edit,
        }

    async def execute(self, request_id: UUID, body: ApprovalBody) -> PurchaseRequestView:
        return await self._handlers[body.action].execute(request_id, body)
