from notification.application.contracts.providers import (
    NotificationProvider,
    NotificationProviderResolver,
)
from notification.application.contracts.templates import MessageTemplateRenderer
from notification.domain.enums import NotificationChannel
from notification.domain.types import JsonValue
from notification.domain.value_objects import RenderedMessage


class UnusedNotificationTemplateRenderer(MessageTemplateRenderer):
    def render(
        self,
        template_key: str,
        locale: str,
        channel: NotificationChannel,
        variables: dict[str, JsonValue],
    ) -> RenderedMessage:
        raise RuntimeError("Notification delivery is not configured in Stage 10.")


class UnusedNotificationProviderResolver(NotificationProviderResolver):
    def resolve(self, channel: NotificationChannel) -> NotificationProvider:
        raise RuntimeError("Notification delivery is not configured in Stage 10.")
