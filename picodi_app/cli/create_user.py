from __future__ import annotations

import argparse
import asyncio
from typing import TYPE_CHECKING, Any

from picodi import Provide, inject
from picodi.helpers import lifespan

from picodi_app.deps import get_user_repository
from picodi_app.user import IUserRepository, User, generate_new_user_id
from picodi_app.utils import hash_password
from picodi_app.weather import Coordinates

if TYPE_CHECKING:
    from collections.abc import Coroutine


# Picodi Note:
#   `lifespan` decorator is used to automatically init and shutdown dependencies
@lifespan
# Picodi Note:
#   With Picodi you can use same dependencies in CLI and API code.
@inject
async def create_user(
    email: str,
    password: str,
    location: Coordinates,
    user_repo: IUserRepository = Provide(get_user_repository),
) -> None:
    new_user = User(
        id=generate_new_user_id(),
        email=email,
        location=location,
        hashed_password=hash_password(password),
    )
    await user_repo.create_user(new_user)


def _validate_location(location: str) -> tuple[float, float]:
    try:
        lat, lon = location.split(",")
        return float(lat), float(lon)
    except ValueError:
        raise SystemExit("ERROR: Invalid location format. Should be 'lat,lon'")


def main(args: list[str] | None = None) -> Coroutine[Any, Any, None]:
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("email", type=str, help="User email")
    parser.add_argument("password", type=str, help="User password")
    parser.add_argument(
        "location",
        type=str,
        help="User location (coordinates in format 'lat,lon'. Example: '50.45,30.52')",
    )
    parsed_args = parser.parse_args(args=args)
    lat, lon = _validate_location(parsed_args.location)
    return create_user(
        parsed_args.email,
        parsed_args.password,
        Coordinates(latitude=lat, longitude=lon),
    )


if __name__ == "__main__":
    asyncio.run(main())
