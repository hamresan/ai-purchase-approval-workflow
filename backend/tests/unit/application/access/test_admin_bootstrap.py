from uuid import UUID

from ai_purchase_workflow.application.access import ApplicationRole, BootstrapFirstAdmin


class RecordingRoleWriter:
    def __init__(self) -> None:
        self.calls: list[tuple[UUID, ApplicationRole]] = []

    async def ensure_role(self, user_id: UUID, role: ApplicationRole) -> None:
        self.calls.append((user_id, role))


async def test_bootstrap_first_admin_grants_admin_role() -> None:
    user_id = UUID("11111111-1111-1111-1111-111111111111")
    writer = RecordingRoleWriter()

    await BootstrapFirstAdmin(writer).execute(user_id)

    assert writer.calls == [(user_id, ApplicationRole.ADMIN)]
