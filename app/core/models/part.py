from typing import Annotated, List, Optional

from bson.objectid import ObjectId
from pydantic import BaseModel, BeforeValidator, Field

from .category import Category

PyObjectId = Annotated[str, BeforeValidator(str)]


class Location(BaseModel):
    room: Optional[str | int] = Field(default=None)
    bookcase: Optional[str | int] = Field(default=None)
    shelf: Optional[str | int] = Field(default=None)
    cubicle: Optional[str | int] = Field(default=None)
    column: Optional[str | int] = Field(default=None)
    row: Optional[str | int] = Field(default=None)


class Part(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    serial_number: str = Field(...)
    name: str = Field(...)
    description: str = Field(...)
    category: Category = Field(...)
    quantity: int = Field(...)
    price: float = Field(...)
    location: Location = Field(...)

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


class PartsCollection(BaseModel):
    parts: List[Part]


class UpdatePart(BaseModel):
    serial_number: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[Category] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    location: Optional[Location] = None

    class Config:
        arbitrary_types_allowed = (True,)
        json_encoders = {ObjectId: str}
