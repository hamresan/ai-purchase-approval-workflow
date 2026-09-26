from ai_purchase_workflow.application.observability import WorkflowObservation, WorkflowObserver
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
        observer: WorkflowObserver,
    ) -> None:
        self._workflow = workflow
        self._state_factory = state_factory
        self._result_mapper = result_mapper
        self._observer = observer

    async def execute(
        self,
        free_text: str,
        *,
        checkpoint_id: str | None = None,
    ) -> PurchaseRequestWorkflowResult:
        state = self._state_factory.create(free_text, checkpoint_id=checkpoint_id)
        self._observer.record(
            WorkflowObservation(
                event="workflow_started",
                workflow_thread_id=state["workflow_id"],
                state_transition="started",
            )
        )
        completed_state = await self._workflow.execute(
            state,
            thread_id=state["workflow_id"],
        )
        result = self._result_mapper.map(completed_state)
        self._observer.record(
            WorkflowObservation(
                event="workflow_completed",
                workflow_thread_id=state["workflow_id"],
                purchase_request_id=result.purchase_request_id,
                state_transition=result.status,
                fallback_occurred=result.needs_human_review,
            )
        )
        return result
