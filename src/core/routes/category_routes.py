from typing import Any, Dict

from beanie import PydanticObjectId
from beanie.exceptions import RevisionIdWasChanged
from beanie.operators import Set
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError

from ..exceptions import CategoryNotFoundException
from ..models.category import Category, UpdateCategory

router: APIRouter = APIRouter()


@router.get(
    "/{category_id}",
    response_description="Get single category",
)
async def get_category(category_id: PydanticObjectId):
    category: Category = await Category.get(category_id)
    if category is not None:
        return JSONResponse(
            {
                "message": f"Category {str(category_id)} retrieved",
                "data": category.model_dump(),
            }
        )
    raise CategoryNotFoundException(category_id)


@router.post(
    "/",
    response_description="Create category",
)
async def create_category(category: Category):
    try:
        new_category: Category = await category.create()
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Category with {e.details.get("keyValue")} already exists',
        )
    created_category: Category = await Category.get(new_category.id)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": f"Category {new_category.id} created",
            "data": created_category.model_dump(),
        },
    )


@router.put("/{category_id}", response_description="Update Category")
async def update_category(
    category_id: PydanticObjectId, data: UpdateCategory = Body(...)
):
    category: Category = await Category.find_one({"_id": category_id})
    if not category:
        raise CategoryNotFoundException(category_id)
    update_data: Dict[str, Any] = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        updated_category: Category = await category.update(Set(update_data))
    except (DuplicateKeyError, RevisionIdWasChanged):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this serial number already exists",
        )

    if updated_category is not None:
        return JSONResponse(
            {
                "message": f"Category {str(category_id)} updated",
                "data": updated_category.model_dump(),
            }
        )
    raise CategoryNotFoundException(category_id)


@router.delete("/{category_id}", response_description="Delete category")
async def delete_category(category_id: PydanticObjectId):
    category: Category = await Category.get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await category.delete()
    return JSONResponse({"message": f"Category {str(category_id)} deleted"})
