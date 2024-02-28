from typing import Any, Dict, List

import pytest
from asgi_lifespan import LifespanManager
from beanie import init_beanie
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient
from pymongo.results import InsertManyResult

import app.core.models as models
from app.core.app import app
from app.core.models.category import Category
from app.core.models.part import Part


async def mock_database():
    client = AsyncMongoMockClient()
    await init_beanie(
        database=client["database_name"],
        recreate_views=True,
        document_models=models.__all__,
    )


@pytest.fixture
async def client(mocker):
    mocker.patch("app.core.database.init_db", return_value=await mock_database())
    async with LifespanManager(app):
        async with AsyncClient(
            app=app, base_url="http://test", follow_redirects=True
        ) as ac:
            yield ac


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def parts():
    parts_data: List[Dict[str, Any]] = [
        {
            "serial_number": "ABC123",
            "name": "Widget",
            "description": "test-object",
            "category": "Electronics",
            "quantity": 10,
            "price": 5.99,
            "location": {
                "room": "A101",
                "bookcase": "B2",
                "shelf": "3",
                "cubicle": None,
                "column": "C",
                "row": 1,
            },
        },
        {
            "serial_number": "DEF456",
            "name": "Gizmo",
            "description": "test-object",
            "category": "Tools",
            "quantity": 5,
            "price": 9.99,
            "location": {
                "room": "B203",
                "bookcase": "B1",
                "column": "D",
            },
        },
        {
            "serial_number": "GHI789",
            "name": "Thingamajig",
            "description": "test-object",
            "category": "Miscellaneous",
            "quantity": 3,
            "price": 3.49,
            "location": {},
        },
        {
            "serial_number": "JKL012",
            "name": "Contraption",
            "description": "test-object",
            "category": "Machinery",
            "quantity": 1,
            "price": 99.99,
            "location": {
                "room": 101,
                "column": "F",
                "row": 3,
            },
        },
        {
            "serial_number": "existing_serial",
            "name": "Doodad",
            "description": "test-object",
            "category": "Art",
            "quantity": 2,
            "price": 7.99,
            "location": {
                "room": "C304",
                "bookcase": "C2",
                "row": "2",
            },
        },
    ]
    parts: InsertManyResult = await Part.insert_many(
        [Part(**part) for part in parts_data]
    )
    yield parts


@pytest.fixture
async def categories():
    category_data: List[Dict[str, Any]] = [
        {"name": "Electronics"},
        {"name": "Tools"},
        {"name": "Miscellaneous"},
        {"name": "Machinery"},
        {"name": "Subcategory", "parent_name": "Electronics"},
        {"name": "existing_category", "parent_name": "Tools"},
    ]
    categories: InsertManyResult = await Category.insert_many(
        [Category(**category) for category in category_data]
    )
    yield categories
