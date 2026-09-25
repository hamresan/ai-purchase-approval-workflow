from uuid import UUID

from ai_purchase_workflow.application.purchase_requests.approval import (
    PurchaseRequestWorkflowGateway,
)
from ai_purchase_workflow.application.workflows import WorkflowThreadRepository
from ai_purchase_workflow.infrastructure.workflows.purchase_request import (
    PurchaseRequestWorkflow,
)


class LangGraphPurchaseRequestWorkflowGateway(PurchaseRequestWorkflowGateway):
    def __init__(
        self,
        workflow: PurchaseRequestWorkflow,
        threads: WorkflowThreadRepository,
    ) -> None:
        self._workflow = workflow
        self._threads = threads

    async def resume_approved(self, request_id: UUID) -> None:
        thread_id = await self._require_thread_id(request_id)
        await self._workflow.resume(thread_id=thread_id, action="approved")

    async def resume_rejected(self, request_id: UUID) -> None:
        thread_id = await self._require_thread_id(request_id)
        await self._workflow.resume(thread_id=thread_id, action="rejected")

    async def _require_thread_id(self, request_id: UUID) -> str:
        thread_id = await self._threads.get_thread_id(request_id)
        if thread_id is None:
            raise LookupError(f"No workflow thread is bound to purchase request {request_id}.")
        return thread_id
