from typing import Annotated

from beanie import Document, Indexed
from pydantic import EmailStr


class User(Document):
    username: Annotated[str, Indexed(unique=True)]
    email: Annotated[EmailStr, Indexed(unique=True)]
    password: str

    class Settings:
        name: str = "users"
