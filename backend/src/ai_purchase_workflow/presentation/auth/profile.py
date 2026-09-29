from dataclasses import dataclass
from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from ai_purchase_workflow.presentation.auth.dependencies import CurrentPrincipalDependency


class UpdateProfileBody(BaseModel):
    full_name: str = Field(min_length=1, max_length=160)


@dataclass(frozen=True, slots=True)
class UpdateProfileEndpoint:
    async def __call__(
        self,
        body: UpdateProfileBody,
        request: Request,
        principal: CurrentPrincipalDependency,
    ) -> dict[str, str]:
        user = await request.app.state.identity.public_api.user_profile_writer.update_full_name(
            principal.user_id,
            body.full_name,
        )
        return {"full_name": user.full_name}


def build_profile_router() -> APIRouter:
    router = APIRouter(prefix="/api/profile", tags=["profile"])
    endpoint = UpdateProfileEndpoint()

    async def update_profile(
        body: UpdateProfileBody,
        request: Request,
        principal: CurrentPrincipalDependency,
    ) -> dict[str, str]:
        return await endpoint(body, request, principal)

    router.add_api_route("", update_profile, methods=["PATCH"], response_model=dict[str, str])
    return router
