from typing import Annotated, List, Optional

from pydantic import BaseModel, BeforeValidator, Field

PyObjectId = Annotated[str, BeforeValidator(str)]


class Category(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    name: str = Field(...)
    parent_name: Optional[str] = Field(default=None)


class CategoryCollection(BaseModel):
    categories: List[Category]


class UpdateCategory(BaseModel):
    name: Optional[str] = None
    parent_name: Optional[str] = None
