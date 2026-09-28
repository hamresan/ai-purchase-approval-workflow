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

    def ensure_not_self_approval(
        self,
        principal: ApplicationPrincipal,
        requester_user_id: str,
    ) -> None:
        if str(principal.user_id) == requester_user_id:
            raise AuthorizationError("Self approval is not allowed.")

    def require_any(
        self,
        principal: ApplicationPrincipal,
        *roles: ApplicationRole,
    ) -> None:
        if principal.roles.isdisjoint(roles):
            raise AuthorizationError("Not authorized.")
