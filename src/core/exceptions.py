from typing import Dict

from beanie import PydanticObjectId
from fastapi import status
from fastapi.exceptions import HTTPException


class PartNotFoundException(HTTPException):
    def __init__(self, part_id: PydanticObjectId):
        detail: Dict[str, str] = {"message": f"Part {str(part_id)} not found"}
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class CategoryNotFoundException(HTTPException):
    def __init__(self, category_id: PydanticObjectId):
        detail: Dict[str, str] = {"message": f"Category {str(category_id)} not found"}
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
