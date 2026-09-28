import argparse
import asyncio
from uuid import UUID

from ai_purchase_workflow.application.access import BootstrapFirstAdmin
from ai_purchase_workflow.composition_root.settings import get_settings
from ai_purchase_workflow.infrastructure.access import SqlAlchemyRoleWriter
from ai_purchase_workflow.infrastructure.persistence import create_session_factory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Grant the ADMIN application role to an existing Identity user."
    )
    parser.add_argument(
        "--user-id",
        required=True,
        type=UUID,
        help="Existing identity user UUID returned by registration or /identity/me.",
    )
    return parser.parse_args()


async def bootstrap_admin(user_id: UUID) -> None:
    settings = get_settings()
    session_factory = create_session_factory(settings.database_url)
    async with session_factory() as session:
        await BootstrapFirstAdmin(SqlAlchemyRoleWriter(session)).execute(user_id)


def main() -> None:
    args = parse_args()
    asyncio.run(bootstrap_admin(args.user_id))


if __name__ == "__main__":
    main()
