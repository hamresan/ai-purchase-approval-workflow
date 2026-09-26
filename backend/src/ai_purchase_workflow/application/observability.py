from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class WorkflowObservation:
    event: str
    workflow_thread_id: str
    purchase_request_id: UUID | None = None
    state_transition: str | None = None
    tool_name: str | None = None
    fallback_occurred: bool = False


class WorkflowObserver(Protocol):
    def record(self, observation: WorkflowObservation) -> None: ...
