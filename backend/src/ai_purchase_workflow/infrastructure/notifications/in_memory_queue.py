from notification.application.contracts.queue import NotificationQueue
from notification.application.dto import NotificationJobPayload
from notification.public import NotificationReference


class InMemoryNotificationQueue(NotificationQueue):
    """Development queue until the durable Stage 13 worker infrastructure is introduced."""

    def __init__(self) -> None:
        self.items: list[NotificationJobPayload] = []

    async def enqueue(self, payload: NotificationJobPayload) -> NotificationReference:
        self.items.append(payload)
        return NotificationReference(job_id=str(len(self.items)))
