import argparse
import asyncio

from picodi import Provide, inject

from picodi_app.deps import get_user_repository
from picodi_app.user import IUserRepository, User, generate_new_user_id
from picodi_app.utils import hash_password
from picodi_app.weather import Coordinates


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
        raise ValueError("Invalid location format. Should be 'lat,lon'")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a new user")
    parser.add_argument("email", type=str, help="User email")
    parser.add_argument("password", type=str, help="User password")
    parser.add_argument(
        "location",
        type=str,
        help="User location (cooridinates in format 'lat,lon'. Example: '50.45,30.52')",
    )
    args = parser.parse_args()
    lat, lon = _validate_location(args.location)
    asyncio.run(
        create_user(args.email, args.password, Coordinates(latitude=lat, longitude=lon))
    )


if __name__ == "__main__":
    main()
