import logging

from notification.application.contracts.queue import NotificationQueue
from notification.application.dto import NotificationJobPayload
from notification.public import NotificationReference

logger = logging.getLogger(__name__)


class DevelopmentNotificationQueue(NotificationQueue):
    """Development-only queue decorator that exposes OTP codes in local logs."""

    def __init__(self, queue: NotificationQueue) -> None:
        self._queue = queue

    async def enqueue(self, payload: NotificationJobPayload) -> NotificationReference:
        if payload.template_key == "identity.otp":
            otp = payload.variables.get("otp")
            logger.warning("Development OTP for %s: %s", payload.recipient, otp)
        return await self._queue.enqueue(payload)
