from typing import Annotated, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class Category(Document):
    name: Annotated[str, Indexed(unique=True)]
    parent_name: Optional[str] = Field(default=None)

    class Settings:
        name = "categories"


class UpdateCategory(BaseModel):
    name: Optional[str] = None
    parent_name: Optional[str] = None
