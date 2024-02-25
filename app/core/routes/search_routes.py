from core.database import category_collection, parts_collection
from core.models.category import CategoryCollection
from core.models.part import PartsCollection
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get(
    "/parts", response_description="List all parts", response_model_by_alias=False
)
async def list_parts():
    parts: PartsCollection = PartsCollection(
        parts=await parts_collection.find().to_list(None)
    )
    return JSONResponse({"data": parts.dict()})


@router.get(
    "/category",
    response_description="List all categories",
    response_model_by_alias=False,
)
async def list_categories():
    categories: CategoryCollection = CategoryCollection(
        categories=await category_collection.find().to_list(None)
    )
    return JSONResponse({"data": categories.dict()})
