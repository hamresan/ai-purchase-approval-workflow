import argparse
import asyncio

from identity.domain import IdentityType

from ai_purchase_workflow.application.access import BootstrapFirstAdmin
from ai_purchase_workflow.composition_root.identity import build_identity_module
from ai_purchase_workflow.composition_root.settings import get_settings
from ai_purchase_workflow.infrastructure.access import SqlAlchemyRoleWriter
from ai_purchase_workflow.infrastructure.persistence import create_session_factory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grant the ADMIN application role to a registered mobile user."
    )
    parser.add_argument(
        "--mobile",
        required=True,
        help="Registered mobile number in international format, for example +96891234567.",
    )
    return parser.parse_args()


async def bootstrap_admin(mobile: str) -> None:
    settings = get_settings()
    session_factory = create_session_factory(settings.database_url)
    identity = build_identity_module(settings, session_factory)
    user_id = await identity.public_api.user_resolver.resolve_user_id(IdentityType.MOBILE, mobile)
    if user_id is None:
        raise SystemExit("No registered Identity user was found for that mobile number.")

    async with session_factory() as session:
        await BootstrapFirstAdmin(SqlAlchemyRoleWriter(session)).execute(user_id)


def main() -> None:
    args = parse_args()
    asyncio.run(bootstrap_admin(args.mobile))


if __name__ == "__main__":
    main()
