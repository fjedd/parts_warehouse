from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from ..auth.jwt_handler import AuthHandler
from ..models.category import Category
from ..models.part import Part

auth_handler: AuthHandler = AuthHandler()
router: APIRouter = APIRouter()


@router.get("/parts", response_description="List all parts")
async def list_parts():
    parts: List[Part] = await Part.all().to_list()
    return JSONResponse({"data": [part.model_dump() for part in parts]})


@router.get("/categories", response_description="List all categories")
async def list_categories(
    # user: Annotated[User, Depends(auth_handler.verify_token)]
):
    categories: List[Category] = await Category.all().to_list()
    return JSONResponse({"data": [category.model_dump() for category in categories]})
