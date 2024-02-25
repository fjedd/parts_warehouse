from typing import Dict

from fastapi import status
from fastapi.exceptions import HTTPException


class PartNotFoundException(HTTPException):
    def __init__(self, part_id: str):
        detail: Dict[str, str] = {"message": f"Part {part_id} not found"}
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class CategoryNotFoundException(HTTPException):
    def __init__(self, part_id: str):
        detail: Dict[str, str] = {"message": f"Category {part_id} not found"}
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
