from typing import Any, Dict

from beanie import PydanticObjectId
from beanie.exceptions import RevisionIdWasChanged
from beanie.operators import Set
from fastapi import APIRouter, Body, HTTPException, status
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError

from ..exceptions import PartNotFoundException
from ..models.part import Part, UpdatePart

router = APIRouter()


@router.get(
    "/{part_id}",
    response_description="Get single part",
    response_model_by_alias=False,
)
async def get_part(part_id: PydanticObjectId):
    part: Part = await Part.get(part_id)
    if part is not None:
        return JSONResponse(
            {"message": f"Part {str(part_id)} retrieved", "data": part.model_dump()}
        )
    raise PartNotFoundException(part_id)


@router.post(
    "/",
    response_description="Create part",
    status_code=status.HTTP_201_CREATED,
)
async def create_part(part: Part):
    try:
        new_part: Part = await part.create()
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'Part with {e.details.get("keyValue")} already exists',
        )
    created_part: Part = await Part.get(new_part.id)
    return JSONResponse(
        {
            "message": f"Part {new_part.id} created",
            "data": created_part.model_dump(),
        }
    )


@router.put("/{part_id}", response_description="Update part")
async def update_part(part_id: PydanticObjectId, data: UpdatePart = Body(...)):
    part: Part = await Part.find_one({"_id": part_id})
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if data.location:
        data.location = part.location.model_copy(
            update=data.location.model_dump(exclude_none=True)
        )
    update_data: Dict[str, Any] = data.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    try:
        updated_part: Part = await part.update(Set(update_data))
    except (DuplicateKeyError, RevisionIdWasChanged):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Part with this serial number already exists",
        )
    if updated_part is not None:
        return JSONResponse(
            {
                "message": f"Part {str(part_id)} updated",
                "data": updated_part.model_dump(),
            }
        )
    raise PartNotFoundException(part_id)


@router.delete("/{part_id}", response_description="Delete part")
async def delete_part(part_id: PydanticObjectId):
    part: Part = await Part.get(part_id)
    if not part:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await part.delete()
    return JSONResponse({"message": f"Part {str(part_id)} deleted"})
