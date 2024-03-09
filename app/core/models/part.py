from typing import Annotated, Optional

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class Location(BaseModel):
    room: Optional[str | int] = Field(default=None)
    bookcase: Optional[str | int] = Field(default=None)
    shelf: Optional[str | int] = Field(default=None)
    cubicle: Optional[str | int] = Field(default=None)
    column: Optional[str | int] = Field(default=None)
    row: Optional[str | int] = Field(default=None)


class Part(Document):
    serial_number: Annotated[str, Indexed(unique=True)]
    name: str
    description: str
    category: str
    quantity: int
    price: float
    location: Location

    class Settings:
        name = "parts"

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "part": {
                "serial_number": "04977fa636994a1eb8cfaada97532549",
                "name": "Capacitor",
                "description": "Lorem ipsum dolor sit amet",
                "category": "electrical",
                "quantity": 10,
                "price": 5.99,
                "location": {"shelf": 10, "room": "storage_2", "row": 12, "column": 6},
            }
        }


class UpdatePart(BaseModel):
    serial_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    location: Optional[Location] = None

    class Config:
        arbitrary_types_allowed = (True,)
