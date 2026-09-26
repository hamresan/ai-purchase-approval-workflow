import logging

from ai_purchase_workflow.application.observability import WorkflowObservation, WorkflowObserver


class LoggingWorkflowObserver(WorkflowObserver):
    def __init__(self, logger: logging.Logger | None = None) -> None:
        self._logger = logger or logging.getLogger("ai_purchase_workflow.workflow")

    def record(self, observation: WorkflowObservation) -> None:
        self._logger.info(
            observation.event,
            extra={
                "workflow_thread_id": observation.workflow_thread_id,
                "purchase_request_id": (
                    str(observation.purchase_request_id)
                    if observation.purchase_request_id is not None
                    else None
                ),
                "state_transition": observation.state_transition,
                "tool_name": observation.tool_name,
                "fallback_occurred": observation.fallback_occurred,
            },
        )
