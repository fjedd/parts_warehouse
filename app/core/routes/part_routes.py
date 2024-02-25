from typing import Any, Dict

from bson.errors import InvalidId
from bson.objectid import ObjectId
from core.database import parts_collection
from core.exceptions import PartNotFoundException
from core.models.part import Location, Part, UpdatePart
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.collection import ReturnDocument
from pymongo.errors import DuplicateKeyError
from pymongo.results import DeleteResult, InsertOneResult

router = APIRouter()


@router.get(
    "/{id}",
    response_description="Get single part",
    response_model_by_alias=False,
)
async def get_part(part_id: str):
    try:
        part: Dict[str, Any] = await parts_collection.find_one(
            {"_id": ObjectId(part_id)}
        )
    except InvalidId:
        raise PartNotFoundException(part_id)
    if part is not None:
        return JSONResponse(
            {"message": f"Part {part_id} retrieved", "data": Part(**part).dict()}
        )
    raise PartNotFoundException(part_id)


@router.post(
    "/",
    response_description="Create part",
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_part(part: Part):
    try:
        new_part: InsertOneResult = await parts_collection.insert_one(
            part.model_dump(by_alias=True, exclude=["id"])
        )
    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Part with this serial number already exists.",
        )
    created_part: Dict[str, Any] = await parts_collection.find_one(
        {"_id": new_part.inserted_id}
    )
    return JSONResponse(
        {
            "message": f"Part {new_part.inserted_id} created",
            "data": Part(**created_part).dict(),
        }
    )


@router.put("/{id}", response_description="Update part")
async def update_part(part_id: str, data: UpdatePart = Body(...)):
    part = await parts_collection.find_one({"_id": ObjectId(part_id)})
    data.location = Location(**part["location"]).copy(
        update=data.location.dict(exclude_none=True)
    )
    update_data: Dict[str, Any] = data.dict(exclude_none=True)
    if len(update_data) >= 1:
        try:
            updated_part: Dict[str, Any] = await parts_collection.find_one_and_update(
                {"_id": ObjectId(part_id)},
                {"$set": update_data},
                return_document=ReturnDocument.AFTER,
            )
        except DuplicateKeyError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Part with this serial number already exists",
            )

        if updated_part is not None:
            return JSONResponse(
                {
                    "message": f"Part {part_id} updated",
                    "data": Part(**updated_part).dict(),
                }
            )
    raise PartNotFoundException(part_id)


@router.delete("/{id}", response_description="Delete part")
async def delete_part(part_id: str):
    try:
        deleted_part: DeleteResult = await parts_collection.delete_one(
            {"_id": ObjectId(part_id)}
        )
    except InvalidId:
        raise PartNotFoundException(part_id)

    if deleted_part.deleted_count == 1:
        return JSONResponse({"message": f"Part {part_id} deleted"})
    raise PartNotFoundException(part_id)
