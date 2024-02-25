from typing import Any, Dict

from bson import ObjectId
from bson.errors import InvalidId
from core.database import category_collection
from core.exceptions import CategoryNotFoundException
from core.models.category import Category, UpdateCategory
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult, InsertOneResult

router = APIRouter()


@router.get(
    "/{id}",
    response_description="Get single category",
    response_model_by_alias=False,
)
async def get_category(category_id: str):
    try:
        category: Dict[str, str] = await category_collection.find_one(
            {"_id": ObjectId(category_id)}
        )
    except InvalidId:
        raise CategoryNotFoundException(category_id)
    if category is not None:
        return JSONResponse(
            {
                "message": f"Category {category_id} retrieved",
                "data": Category(**category).dict(),
            }
        )
    raise CategoryNotFoundException(category_id)


@router.post(
    "/",
    response_description="Create category",
    response_model_by_alias=False,
)
async def create_category(category: Category):
    try:
        new_category: InsertOneResult = await category_collection.insert_one(
            category.model_dump(by_alias=True, exclude=["id"])
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this name already exists.",
        )
    created_category: Dict[str, Any] = await category_collection.find_one(
        {"_id": new_category.inserted_id}
    )
    return JSONResponse(
        {
            "message": f"Category {new_category.inserted_id} created",
            "data": Category(**created_category).dict(),
        }
    )


@router.put("/{id}", response_description="Update Category")
async def update_category(category_id: str, data: UpdateCategory = Body(...)):
    update_data: Dict[str, Any] = data.dict(exclude_none=True)
    if len(update_data) >= 1:
        try:
            updated_category: Dict[
                str, Any
            ] = await category_collection.find_one_and_update(
                {"_id": ObjectId(category_id)},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )
        if updated_category is not None:
            return JSONResponse(
                {
                    "message": f"Category {category_id} updated",
                    "data": Category(**updated_category).dict(),
                }
            )
    raise CategoryNotFoundException(category_id)


@router.delete("/{id}", response_description="Delete category")
async def delete_category(category_id: str):
    try:
        deleted_category: DeleteResult = await category_collection.delete_one(
            {"_id": ObjectId(category_id)}
        )
    except InvalidId:
        raise CategoryNotFoundException(category_id)

    if deleted_category.deleted_count == 1:
        return JSONResponse({"message": f"Category {category_id} deleted"})
    raise CategoryNotFoundException(category_id)
