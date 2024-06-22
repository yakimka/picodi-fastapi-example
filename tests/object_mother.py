from picodi_app.user import User
from picodi_app.utils import hash_password
from picodi_app.weather import Coordinates


class ObjectMother:  # noqa: PIE798
    @classmethod
    def create_user(
        cls,
        id: str = "00000000000000000000000000000001",
        email: str = "test_user@localhost.localhost",
        location: Coordinates | None = None,
        password: str = "12345678",
    ):
        if location is None:
            location = Coordinates(latitude=50.1, longitude=30.1)
        return User(
            id=id,
            email=email,
            location=location,
            hashed_password=cls.create_hashed_password(password),
        )

    @classmethod
    def create_hashed_password(cls, password: str) -> str:
        return hash_password(password)
