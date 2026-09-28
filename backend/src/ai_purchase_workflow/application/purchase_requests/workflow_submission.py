from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.dto import PurchaseRequestView
from ai_purchase_workflow.application.purchase_requests.repository import PurchaseRequestRepository
from ai_purchase_workflow.application.purchase_requests.use_cases import GetPurchaseRequest


@dataclass(frozen=True, slots=True)
class PurchaseRequestWorkflowStartResult:
    purchase_request_id: UUID | None
    review_reason: str | None = None


class PurchaseRequestWorkflowStarter(Protocol):
    async def start(self, free_text: str) -> PurchaseRequestWorkflowStartResult: ...


class PurchaseRequestWorkflowReviewRequiredError(Exception):
    """The free-text workflow could not create a reviewable purchase request."""


@dataclass(frozen=True, slots=True)
class SubmitFreeTextPurchaseRequestCommand:
    request_text: str
    requester_name: str | None = None
    requester_user_id: UUID | None = None


class SubmitFreeTextPurchaseRequest:
    def __init__(
        self,
        workflow: PurchaseRequestWorkflowStarter,
        get_purchase_request: GetPurchaseRequest,
        repository: PurchaseRequestRepository,
    ) -> None:
        self._workflow = workflow
        self._get_purchase_request = get_purchase_request
        self._repository = repository

    async def execute(
        self,
        command: SubmitFreeTextPurchaseRequestCommand,
    ) -> PurchaseRequestView:
        free_text = command.request_text
        if command.requester_name:
            free_text = f"Requester: {command.requester_name}\nRequest: {command.request_text}"

        result = await self._workflow.start(free_text)
        if result.purchase_request_id is None:
            fallback_detail = "The request needs more information before it can continue."
            raise PurchaseRequestWorkflowReviewRequiredError(
                result.review_reason or fallback_detail
            )
        request = await self._repository.get(result.purchase_request_id)
        if request is not None:
            request.requester_name = command.requester_name
            request.requester_user_id = command.requester_user_id
            await self._repository.save(request)
        return await self._get_purchase_request.execute(result.purchase_request_id)
