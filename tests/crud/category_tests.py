import json
from typing import Any, Dict

import pytest
from beanie import PydanticObjectId
from fastapi import status
from httpx import AsyncClient, Response
from pymongo.results import InsertManyResult

from app.core.models.category import Category


@pytest.mark.anyio
async def test_get_single_category(client: AsyncClient, categories: InsertManyResult):
    # Arrange
    category_id: PydanticObjectId = categories.inserted_ids[0]
    expected_message: str = f"Category {category_id} retrieved"
    # Act
    response: Response = await client.get(f"/categories/{category_id}")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert json.loads(response.content)["message"] == expected_message


@pytest.mark.parametrize(
    "invalid_id", [0, 123, 2.5, " ", "asd", "null", None, [], {}, ()]
)
@pytest.mark.anyio
async def test_get_single_category_invalid_id_type(
    client: AsyncClient, categories: InsertManyResult, invalid_id: Any
):
    # Arrange
    expected_message: str = "Value error, Id must be of type PydanticObjectId"
    # Act
    response: Response = await client.get(f"/categories/{invalid_id}")
    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == expected_message


@pytest.mark.anyio
async def test_get_single_category_do_not_exist(
    client: AsyncClient, categories: InsertManyResult
):
    # Arrange
    category_id: PydanticObjectId = PydanticObjectId()
    expected_message: str = f"Category {category_id} not found"
    # Act
    response: Response = await client.get(f"/categories/{category_id}")
    # Assert
    assert category_id not in categories.inserted_ids
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"]["message"] == expected_message


@pytest.mark.anyio
async def test_get_all_categories(client: AsyncClient, categories: InsertManyResult):
    # Arrange
    total_categories: int = len(categories.inserted_ids)
    # Act
    response: Response = await client.get("/search/categories")
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert total_categories == len(response.json()["data"])


@pytest.mark.parametrize(
    "update_data",
    [
        {
            "name": "test-update",
            "parent_name": "Tools",
        },
        {
            "name": "test-update",
        },
    ],
)
@pytest.mark.anyio
async def test_update_category_correct_data(
    client: AsyncClient, categories: InsertManyResult, update_data: Dict[str, Any]
):
    # Arrange
    category_id: PydanticObjectId = categories.inserted_ids[0]
    expected_response: str = f"Category {category_id} updated"
    # Act
    response: Response = await client.put(
        f"/categories/{category_id}", content=json.dumps(update_data)
    )
    updated_category: Category = await Category.get(category_id)
    for key, value in update_data.items():
        if hasattr(updated_category, key):
            if getattr(updated_category, key) != value:
                raise AssertionError

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == expected_response


@pytest.mark.parametrize(
    "update_data, expected_status_code",
    [
        ({}, status.HTTP_400_BAD_REQUEST),
        ({"name": "existing_category"}, status.HTTP_409_CONFLICT),
        (None, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ([], status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("asdf", status.HTTP_422_UNPROCESSABLE_ENTITY),
        (123, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ("null", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
@pytest.mark.anyio
async def test_update_category_invalid_data(
    client: AsyncClient,
    categories: InsertManyResult,
    update_data: Any,
    expected_status_code: status,
):
    # Arrange
    category_id: PydanticObjectId = categories.inserted_ids[0]
    # Act
    response: Response = await client.put(
        f"/categories/{category_id}", content=json.dumps(update_data)
    )
    # Assert
    assert response.status_code == expected_status_code


@pytest.mark.anyio
async def test_delete_category(
    client: AsyncClient,
    categories: InsertManyResult,
):
    # Arrange
    total_categories: int = len(categories.inserted_ids)
    category_id: PydanticObjectId = categories.inserted_ids[0]
    expected_message: str = f"Category {category_id} deleted"
    # Act
    response: Response = await client.delete(f"/categories/{category_id}")
    total_categories_after: int = len(await Category.all().to_list())
    # Assert
    assert total_categories_after == total_categories - 1
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == expected_message


@pytest.mark.anyio
async def test_delete_category_invalid_id(
    client: AsyncClient,
    categories: InsertManyResult,
):
    # Arrange
    total_categories: int = len(categories.inserted_ids)
    category_id: PydanticObjectId = PydanticObjectId()
    # Act
    response: Response = await client.delete(f"/categories/{category_id}")
    total_categories_after: int = len(await Category.all().to_list())
    # Assert
    assert total_categories_after == total_categories
    assert response.status_code == status.HTTP_404_NOT_FOUND
