from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowState


class ResumeOnlyExtractNode:
    async def __call__(
        self,
        _state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        raise RuntimeError("Extraction cannot run while resuming an existing workflow.")


class ResumeOnlyPrepareNode:
    async def __call__(
        self,
        _state: PurchaseRequestWorkflowState,
    ) -> PurchaseRequestWorkflowState:
        raise RuntimeError("Preparation cannot run while resuming an existing workflow.")
