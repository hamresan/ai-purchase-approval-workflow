from uuid import uuid4

from tests.unit.infrastructure.workflows.fakes.observer import FakeWorkflowObserver

from ai_purchase_workflow.application.observability import WorkflowObservation


def test_workflow_observer_keeps_structured_safe_metadata() -> None:
    observer = FakeWorkflowObserver()
    request_id = uuid4()
    observation = WorkflowObservation(
        event="workflow_tool_completed",
        workflow_thread_id="thread-123",
        purchase_request_id=request_id,
        state_transition="pending_approval",
        tool_name="check_budget",
        fallback_occurred=False,
    )

    observer.record(observation)

    assert observer.observations == [observation]
    assert observation.workflow_thread_id == "thread-123"
    assert observation.purchase_request_id == request_id
    assert observation.tool_name == "check_budget"
    assert observation.fallback_occurred is False
