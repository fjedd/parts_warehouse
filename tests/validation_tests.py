import json
from typing import Any, Dict

import pytest
from beanie.operators import Set
from fastapi import status
from httpx import AsyncClient, Response
from pymongo.results import InsertManyResult

from src.core.models.category import Category
from src.core.models.part import Part

from .conftest import mock_no_authentication


class TestValidationNoAuth:
    @classmethod
    def setup_class(cls):
        mock_no_authentication()

    @pytest.mark.anyio
    async def test_delete_category_with_child(
        self, client: AsyncClient, categories: InsertManyResult
    ):
        # Arrange
        expected_response: str = "Could not modify category with children"
        child_category: Category = await Category.find_one(
            {"parent_name": {"$ne": None}}
        )
        parent_category: Category = await Category.find_one(
            {"name": child_category.parent_name}
        )
        # Act
        response: Response = await client.delete(f"/categories/{parent_category.id}")
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response

    @pytest.mark.anyio
    async def test_update_category_with_child(
        self, client: AsyncClient, categories: InsertManyResult
    ):
        # Arrange
        expected_response: str = "Could not modify category with children"
        child_category: Category = await Category.find_one(
            {"parent_name": {"$ne": None}}
        )
        parent_category: Category = await Category.find_one(
            {"name": child_category.parent_name}
        )
        # Act
        response: Response = await client.put(
            f"/categories/{parent_category.id}", content=json.dumps({"name": "asd"})
        )
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response

    @pytest.mark.anyio
    async def test_delete_category_with_assigned_part(
        self, client: AsyncClient, categories: InsertManyResult, parts: InsertManyResult
    ):
        # Arrange
        expected_response: str = "Could not modify category assigned to parts"
        category: Category = await Category.find_one({"parent_name": {"$ne": None}})
        part: Part = await Part.get(parts.inserted_ids[0])
        await part.update(Set({"category": category.name}))
        # Act
        response: Response = await client.delete(f"/categories/{category.id}")
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response

    @pytest.mark.anyio
    async def test_create_part_category_not_exists(
        self, client: AsyncClient, categories: InsertManyResult
    ):
        # Arrange
        category: Category = await Category.find_one({"parent_name": {"$ne": None}})
        part_data: Dict[str, Any] = {
            "serial_number": "TEST123",
            "name": "Doodad",
            "description": "",
            "category": category.name,
            "quantity": 2,
            "price": 7.99,
            "location": {},
        }
        expected_response: str = (
            f'Could not assign part to category "{category.name}" do not exist'
        )
        await category.delete()
        # Act
        response: Response = await client.post("/parts", content=json.dumps(part_data))
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response

    @pytest.mark.anyio
    async def test_create_part_with_base_category(
        self, client: AsyncClient, categories: InsertManyResult
    ):
        # Arrange
        category: Category = await Category.find_one({"parent_name": {"$eq": None}})
        part_data: Dict[str, Any] = {
            "serial_number": "TEST123",
            "name": "Doodad",
            "description": "",
            "category": category.name,
            "quantity": 2,
            "price": 7.99,
            "location": {},
        }
        expected_response: str = (
            f'Could not assign part to base category "{category.name}"'
        )
        # Act
        response: Response = await client.post("/parts", content=json.dumps(part_data))
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response

    @pytest.mark.anyio
    async def test_update_part_category_not_exists(
        self, client: AsyncClient, parts: InsertManyResult, categories: InsertManyResult
    ):
        # Arrange
        category_data: Dict[str, Any] = {"name": "test-cat", "parent_name": "Tools"}
        category: Category = await Category(**category_data).create()
        update_data: Dict[str, Any] = {"category": category.name}
        expected_response: str = (
            f'Could not assign part to category "{category.name}" do not exist'
        )
        await category.delete()
        # Act
        response: Response = await client.put(
            f"/parts/{parts.inserted_ids[0]}", content=json.dumps(update_data)
        )
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response

    @pytest.mark.anyio
    async def test_update_part_with_base_category(
        self, client: AsyncClient, parts: InsertManyResult, categories: InsertManyResult
    ):
        # Arrange
        category: Category = await Category.find_one({"parent_name": {"$eq": None}})
        update_data: Dict[str, Any] = {"category": category.name}
        expected_response: str = (
            f'Could not assign part to base category "{category.name}"'
        )
        # Act
        response: Response = await client.put(
            f"/parts/{parts.inserted_ids[0]}", content=json.dumps(update_data)
        )
        # Assert
        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json()["detail"] == expected_response
