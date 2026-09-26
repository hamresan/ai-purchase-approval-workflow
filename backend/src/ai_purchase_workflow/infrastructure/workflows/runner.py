from ai_purchase_workflow.infrastructure.workflows.purchase_request import (
    PurchaseRequestWorkflow,
)
from ai_purchase_workflow.infrastructure.workflows.result_mapper import (
    PurchaseRequestWorkflowResultMapper,
)
from ai_purchase_workflow.infrastructure.workflows.state import PurchaseRequestWorkflowResult
from ai_purchase_workflow.infrastructure.workflows.state_factory import (
    PurchaseRequestWorkflowStateFactory,
)


class PurchaseRequestWorkflowRunner:
    def __init__(
        self,
        workflow: PurchaseRequestWorkflow,
        state_factory: PurchaseRequestWorkflowStateFactory,
        result_mapper: PurchaseRequestWorkflowResultMapper,
    ) -> None:
        self._workflow = workflow
        self._state_factory = state_factory
        self._result_mapper = result_mapper

    async def execute(
        self,
        free_text: str,
        *,
        checkpoint_id: str | None = None,
    ) -> PurchaseRequestWorkflowResult:
        state = self._state_factory.create(free_text, checkpoint_id=checkpoint_id)
        completed_state = await self._workflow.execute(
            state,
            thread_id=state["workflow_id"],
        )
        return self._result_mapper.map(completed_state)
