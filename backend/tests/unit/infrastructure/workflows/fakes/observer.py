from ai_purchase_workflow.application.observability import WorkflowObservation, WorkflowObserver


class FakeWorkflowObserver(WorkflowObserver):
    def __init__(self) -> None:
        self.observations: list[WorkflowObservation] = []

    def record(self, observation: WorkflowObservation) -> None:
        self.observations.append(observation)
