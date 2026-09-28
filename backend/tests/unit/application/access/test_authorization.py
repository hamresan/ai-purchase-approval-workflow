from uuid import UUID

import pytest

from ai_purchase_workflow.application.access import (
    ApplicationPrincipal,
    ApplicationRole,
    AuthorizationError,
    AuthorizationPolicy,
)

REQUESTER_ID = UUID("11111111-1111-1111-1111-111111111111")
OTHER_USER_ID = UUID("22222222-2222-2222-2222-222222222222")
SESSION_ID = UUID("33333333-3333-3333-3333-333333333333")


def principal(*roles: ApplicationRole, user_id: UUID = REQUESTER_ID) -> ApplicationPrincipal:
    return ApplicationPrincipal(
        user_id=user_id,
        session_id=SESSION_ID,
        display_name="Test User",
        roles=frozenset(roles),
    )


def test_requester_role_can_create_and_modify_own_request() -> None:
    policy = AuthorizationPolicy()
    requester = principal(ApplicationRole.REQUESTER)

    policy.require_requester(requester)
    policy.require_request_owner(requester, REQUESTER_ID)


def test_requester_cannot_modify_another_users_request() -> None:
    policy = AuthorizationPolicy()

    with pytest.raises(AuthorizationError, match="Not authorized to modify"):
        policy.require_request_owner(principal(ApplicationRole.REQUESTER), OTHER_USER_ID)


def test_approver_can_read_requests_but_cannot_perform_requester_mutations() -> None:
    policy = AuthorizationPolicy()
    approver = principal(ApplicationRole.APPROVER)

    policy.require_request_access(approver, OTHER_USER_ID)
    with pytest.raises(AuthorizationError, match="Not authorized"):
        policy.require_request_owner(approver, OTHER_USER_ID)


def test_admin_can_access_requester_and_approver_operations() -> None:
    policy = AuthorizationPolicy()
    admin = principal(ApplicationRole.ADMIN)

    policy.require_requester(admin)
    policy.require_approver(admin)
    policy.require_admin(admin)
    policy.require_request_access(admin, OTHER_USER_ID)
    policy.require_request_owner(admin, OTHER_USER_ID)


def test_requester_cannot_approve() -> None:
    policy = AuthorizationPolicy()

    with pytest.raises(AuthorizationError, match="Not authorized"):
        policy.require_approver(principal(ApplicationRole.REQUESTER))


def test_self_approval_is_rejected_for_approver() -> None:
    policy = AuthorizationPolicy()

    with pytest.raises(AuthorizationError, match="Self approval is not allowed"):
        policy.ensure_not_self_approval(
            principal(ApplicationRole.APPROVER),
            REQUESTER_ID,
        )


def test_approver_can_approve_another_users_request() -> None:
    AuthorizationPolicy().ensure_not_self_approval(
        principal(ApplicationRole.APPROVER),
        OTHER_USER_ID,
    )
