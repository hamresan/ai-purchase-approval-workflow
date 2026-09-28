from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from identity.public import AccessTokenAuthenticationError
from sqlalchemy.ext.asyncio import AsyncSession

from ai_purchase_workflow.application.access import ApplicationPrincipal
from ai_purchase_workflow.infrastructure.access import SqlAlchemyRoleReader
from ai_purchase_workflow.presentation.dependencies import get_session

bearer = HTTPBearer(auto_error=False)
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]
SessionDependency = Annotated[AsyncSession, Depends(get_session)]


async def get_current_principal(
    request: Request,
    session: SessionDependency,
    credentials: BearerCredentials,
) -> ApplicationPrincipal:
    if credentials is None:
        if request.app.state.settings.app_env == "test":
            test_principal = getattr(request.app.state, "e2e_principal", None)
            if test_principal is not None:
                return test_principal
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        identity_principal = (
            await request.app.state.identity.public_api.access_token_authenticator.authenticate(
                credentials.credentials
            )
        )
    except AccessTokenAuthenticationError as error:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Invalid authentication credentials",
        ) from error

    roles = await SqlAlchemyRoleReader(session).get_roles(identity_principal.user_id)
    return ApplicationPrincipal(
        user_id=identity_principal.user_id,
        session_id=identity_principal.session_id,
        display_name=str(identity_principal.user_id),
        roles=roles,
    )


CurrentPrincipalDependency = Annotated[ApplicationPrincipal, Depends(get_current_principal)]
