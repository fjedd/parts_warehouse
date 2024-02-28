import json
from typing import Any, Dict

import pytest
from beanie import PydanticObjectId
from fastapi import status
from httpx import AsyncClient, Response
from pymongo.results import InsertManyResult

from app.core.models.part import Part


@pytest.mark.anyio
async def test_get_single_part(client: AsyncClient, parts: InsertManyResult):
    # Arrange
    part_id: PydanticObjectId = parts.inserted_ids[0]
    expected_message: str = f"Part {part_id} retrieved"
    # Act
    response: Response = await client.get(f"/parts/{part_id}")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content)["message"] == expected_message


@pytest.mark.parametrize(
    "invalid_id", [0, 123, 2.5, " ", "asd", "null", None, [], {}, ()]
)
@pytest.mark.anyio
async def test_get_single_part_invalid_id_type(
    client: AsyncClient, parts: InsertManyResult, invalid_id: Any
):
    # Arrange
    expected_message: str = "Value error, Id must be of type PydanticObjectId"
    # Act
    response: Response = await client.get(f"/parts/{invalid_id}")
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == expected_message


@pytest.mark.anyio
async def test_get_single_part_do_not_exist(
    client: AsyncClient, parts: InsertManyResult
):
    # Arrange
    part_id: PydanticObjectId = PydanticObjectId()
    expected_message: str = f"Part {part_id} not found"
    # Act
    response: Response = await client.get(f"/parts/{part_id}")
    # Assert
    assert part_id not in parts.inserted_ids
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["message"] == expected_message


@pytest.mark.anyio
async def test_get_all_parts(client: AsyncClient, parts: InsertManyResult):
    # Arrange
    total_parts: int = len(parts.inserted_ids)
    # Act
    response: Response = await client.get("/search/parts")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert total_parts == len(response.json()["data"])


@pytest.mark.parametrize(
    "update_data",
    [
        {
            "name": "test-update",
            "description": "test-update",
            "category": "test-update",
            "quantity": 15,
            "price": 30,
            "location": {"room": "test", "bookcase": 12, "column": "test"},
        },
        {"location": {}},
        {
            "serial_number": "new_serial",
            "name": "new_name",
            "description": "test-object",
            "category": "Tools",
            "quantity": 15,
            "price": 9.99,
            "location": {
                "room": "B203",
                "bookcase": "B1",
                "column": "D",
            },
        },
    ],
)
@pytest.mark.anyio
async def test_update_part_correct_data(
    client: AsyncClient, parts: InsertManyResult, update_data: Dict[str, Any]
):
    # Arrange
    part_id: PydanticObjectId = parts.inserted_ids[0]
    expected_response: str = f"Part {part_id} updated"
    # Act
    response: Response = await client.put(
        f"/parts/{part_id}", content=json.dumps(update_data)
    )
    updated_part: Part = await Part.get(part_id)
    for key, value in update_data.items():
        if hasattr(updated_part, key):
            if key == "location":
                for location_key, location_value in value.items():
                    if hasattr(updated_part.location, location_key):
                        if (
                            getattr(updated_part.location, location_key)
                            != location_value
                        ):
                            raise AssertionError
                continue
            if getattr(updated_part, key) != value:
                raise AssertionError

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == expected_response


@pytest.mark.parametrize(
    "update_data, expected_status_code",
    [
        ({}, status.HTTP_400_BAD_REQUEST),
        ({"serial_number": "existing_serial"}, status.HTTP_409_CONFLICT),
        (None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ([], status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("asdf", status.HTTP_422_UNPROCESSABLE_ENTITY),
        (123, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("null", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
@pytest.mark.anyio
async def test_update_part_invalid_data(
    client: AsyncClient,
    parts: InsertManyResult,
    update_data: Any,
    expected_status_code: status,
):
    # Arrange
    part_id: PydanticObjectId = parts.inserted_ids[0]
    # Act
    response: Response = await client.put(
        f"/parts/{part_id}", content=json.dumps(update_data)
    )
    # Assert
    assert response.status_code == expected_status_code


@pytest.mark.anyio
async def test_delete_part(
    client: AsyncClient,
    parts: InsertManyResult,
):
    # Arrange
    total_parts: int = len(parts.inserted_ids)
    part_id: PydanticObjectId = parts.inserted_ids[0]
    expected_message: str = f"Part {part_id} deleted"
    # Act
    response: Response = await client.delete(f"/parts/{part_id}")
    total_parts_after: int = len(await Part.all().to_list())
    # Assert
    assert total_parts_after == total_parts - 1
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == expected_message


@pytest.mark.anyio
async def test_delete_part_invalid_id(
    client: AsyncClient,
    parts: InsertManyResult,
):
    # Arrange
    total_parts: int = len(parts.inserted_ids)
    part_id: PydanticObjectId = PydanticObjectId()
    # Act
    response: Response = await client.delete(f"/parts/{part_id}")
    total_parts_after: int = len(await Part.all().to_list())
    # Assert
    assert total_parts_after == total_parts
    assert response.status_code == status.HTTP_404_NOT_FOUND
