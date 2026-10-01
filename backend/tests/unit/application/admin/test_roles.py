from uuid import UUID

import pytest
from tests.unit.application.admin.fake_role_assignment_repository import (
    FakeRoleAssignmentRepository,
)

from ai_purchase_workflow.application.access import ApplicationRole
from ai_purchase_workflow.application.admin import ManageRoleAssignments, RoleAssignment


@pytest.mark.asyncio
async def test_role_management_delegates_to_repository() -> None:
    repository = FakeRoleAssignmentRepository()
    manager = ManageRoleAssignments(repository)
    user_id = UUID("11111111-1111-1111-1111-111111111111")
    roles = frozenset({ApplicationRole.REQUESTER, ApplicationRole.APPROVER})

    updated = await manager.replace_roles(user_id, roles)

    assert updated == RoleAssignment(user_id, roles)
    assert await manager.list_assignments() == (updated,)
