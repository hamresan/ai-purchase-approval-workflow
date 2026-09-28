from dataclasses import dataclass

from identity.application.dto import AuthSessionResult, VerifyOtpCommand
from identity.public import OtpVerifier

from ai_purchase_workflow.application.access import ApplicationRole, RoleWriter


@dataclass(frozen=True, slots=True)
class RegistrationRoleProvisioningOtpVerifier(OtpVerifier):
    verifier: OtpVerifier
    role_writer: RoleWriter

    async def execute(self, command: VerifyOtpCommand) -> AuthSessionResult:
        result = await self.verifier.execute(command)
        if command.full_name is not None:
            await self.role_writer.ensure_role(result.user_id, ApplicationRole.REQUESTER)
        return result
