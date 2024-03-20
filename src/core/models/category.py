from typing import Annotated, Optional

from beanie import Delete, Document, Indexed, Insert, Update, before_event
from fastapi import HTTPException, status
from pydantic import BaseModel


class Category(Document):
    name: Annotated[str, Indexed(unique=True)]
    parent_name: str | None = None

    @before_event(Insert, Update)
    async def parent_category_exists(self):
        if self.parent_name is not None:
            parent_category: Category = await Category.find_one(
                {"name": self.parent_name}
            )
            if not parent_category or self == parent_category:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Could not assign category to "{self.parent_name}"',
                )

    @before_event(Delete, Update)
    async def children_categories_exists(self):
        children_categories: Category = await Category.find_one(
            {"parent_name": self.name}
        )
        if children_categories:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not modify category with children",
            )

    @before_event(Delete, Update)
    async def part_with_category_exists(self):
        from .part import Part

        part: Part = await Part.find_one({"category": self.name})
        if part:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Could not modify category assigned to parts",
            )

    class Settings:
        name: str = "categories"


class UpdateCategory(BaseModel):
    name: Optional[str] = None
    parent_name: Optional[str] = None
