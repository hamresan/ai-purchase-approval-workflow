from typing import Protocol

from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class WorkflowNode(Protocol):
    async def __call__(
        self,
        state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState: ...
