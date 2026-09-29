from uuid import UUID

from ai_purchase_workflow.application.access.principal import ApplicationPrincipal
from ai_purchase_workflow.application.access.roles import ApplicationRole


class AuthorizationError(PermissionError):
    pass


class AuthorizationPolicy:
    def require_requester(self, principal: ApplicationPrincipal) -> None:
        self.require_any(principal, ApplicationRole.REQUESTER, ApplicationRole.ADMIN)

    def require_approver(self, principal: ApplicationPrincipal) -> None:
        self.require_any(principal, ApplicationRole.APPROVER, ApplicationRole.ADMIN)

    def require_admin(self, principal: ApplicationPrincipal) -> None:
        self.require_any(principal, ApplicationRole.ADMIN)

    def require_request_owner(
        self,
        principal: ApplicationPrincipal,
        requester_user_id: UUID | None,
    ) -> None:
        if ApplicationRole.ADMIN in principal.roles:
            return
        self.require_requester(principal)
        if requester_user_id != principal.user_id:
            raise AuthorizationError("Not authorized to modify this purchase request.")

    def require_request_access(
        self,
        principal: ApplicationPrincipal,
        requester_user_id: UUID | None,
    ) -> None:
        if ApplicationRole.ADMIN in principal.roles or ApplicationRole.APPROVER in principal.roles:
            return
        self.require_requester(principal)
        if requester_user_id != principal.user_id:
            raise AuthorizationError("Not authorized to access this purchase request.")

    def ensure_not_self_approval(
        self,
        principal: ApplicationPrincipal,
        requester_user_id: UUID | None,
    ) -> None:
        if requester_user_id is not None and principal.user_id == requester_user_id:
            raise AuthorizationError("Self approval is not allowed.")

    def require_any(
        self,
        principal: ApplicationPrincipal,
        *roles: ApplicationRole,
    ) -> None:
        if principal.roles.isdisjoint(roles):
            raise AuthorizationError("Not authorized.")
