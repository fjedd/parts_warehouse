from typing import Annotated, Optional

from beanie import Document, Indexed, Insert, Update, after_event, before_event
from fastapi import HTTPException, status
from pydantic import BaseModel


class Location(BaseModel):
    room: Optional[str | int] = None
    bookcase: Optional[str | int] = None
    shelf: Optional[str | int] = None
    cubicle: Optional[str | int] = None
    column: Optional[str | int] = None
    row: Optional[str | int] = None


class Part(Document):
    serial_number: Annotated[str, Indexed(unique=True)]
    name: str
    description: str
    category: str
    quantity: int
    price: float
    location: Location

    @before_event(Insert)
    async def validate_category_exists(self):
        from .category import Category

        category: Category = await Category.find_one({"name": self.category})
        if not category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Could not assign part to category "{self.category}" do not exist',
            )
        if not category.parent_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Could not assign part to base category "{self.category}"',
            )

    @after_event(Update)
    async def validate_category_is_not_base(self):
        from .category import Category

        category: Category = await Category.find_one({"name": self.category})
        if not category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Could not assign part to category "{self.category}" do not exist',
            )
        if not category.parent_name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Could not assign part to base category "{self.category}"',
            )

    class Settings:
        name: str = "parts"


class UpdatePart(BaseModel):
    serial_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    location: Optional[Location] = None
