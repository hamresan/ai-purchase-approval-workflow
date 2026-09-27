from dataclasses import dataclass

from ai_purchase_workflow.application.purchase_requests.dto import PurchaseRequestView
from ai_purchase_workflow.application.purchase_requests.use_cases import GetPurchaseRequest
from ai_purchase_workflow.infrastructure.workflows import PurchaseRequestWorkflowRunner


class PurchaseRequestWorkflowReviewRequiredError(Exception):
    """The free-text workflow could not create a reviewable purchase request."""


@dataclass(frozen=True, slots=True)
class SubmitFreeTextPurchaseRequestCommand:
    request_text: str
    requester_name: str | None = None


class SubmitFreeTextPurchaseRequest:
    def __init__(
        self,
        workflow: PurchaseRequestWorkflowRunner,
        get_purchase_request: GetPurchaseRequest,
    ) -> None:
        self._workflow = workflow
        self._get_purchase_request = get_purchase_request

    async def execute(
        self,
        command: SubmitFreeTextPurchaseRequestCommand,
    ) -> PurchaseRequestView:
        free_text = command.request_text
        if command.requester_name:
            free_text = f"Requester: {command.requester_name}\nRequest: {command.request_text}"

        result = await self._workflow.execute(free_text)
        if result.purchase_request_id is None:
            fallback_detail = "The request needs more information before it can continue."
            raise PurchaseRequestWorkflowReviewRequiredError(
                result.review_reason or fallback_detail
            )
        return await self._get_purchase_request.execute(result.purchase_request_id)
