from typing import Any, Dict, List

import pytest
from asgi_lifespan import LifespanManager
from beanie import init_beanie
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient
from pymongo.results import InsertManyResult

import src.core.models as models
from src.core.app import app, auth_handler
from src.core.models.auth.user import User
from src.core.models.category import Category
from src.core.models.part import Part


async def mock_database():
    client: AsyncMongoMockClient = AsyncMongoMockClient()
    await init_beanie(
        database=client["database_name"],
        document_models=models.__all__,
    )


@pytest.fixture
async def client(mocker):
    mocker.patch(
        "src.core.database.Database.init_db", return_value=await mock_database()
    )
    async with LifespanManager(app):
        async with AsyncClient(
            app=app, base_url="http://test", follow_redirects=True
        ) as ac:
            yield ac


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def mock_no_authentication() -> None:
    app.dependency_overrides[auth_handler.verify_token] = lambda: {}  # type: ignore


@pytest.fixture
async def user():
    user_data: Dict[str, Any] = {
        "username": "test",
        "email": "test@test.com",
        "password": "test",
    }
    user: User = await User(
        username=user_data["username"],
        email=user_data["email"],
        password=auth_handler.get_password_hash(user_data["password"]),
    ).create()
    user_data["user_id"] = user.id
    yield user_data


@pytest.fixture
async def token(user: Dict[str, Any]):
    token: str = auth_handler.encode_token(user["user_id"])
    yield token


@pytest.fixture
async def expired_token(user: Dict[str, Any]):
    token: str = auth_handler.encode_token(user["user_id"], expire_time=-1)
    yield token


@pytest.fixture
async def parts(categories):
    parts_data: List[Dict[str, Any]] = [
        {
            "serial_number": "ABC123",
            "name": "Widget",
            "description": "test-object",
            "category": "SubTools",
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
            "category": "SubTools",
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
            "category": "SubTools2",
            "quantity": 3,
            "price": 3.49,
            "location": {},
        },
        {
            "serial_number": "JKL012",
            "name": "Contraption",
            "description": "test-object",
            "category": "SubElectronics",
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
            "category": "SubMachinery",
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
        {"name": "Miscellaneous"},
        {"name": "Electronics"},
        {"name": "Machinery"},
        {"name": "Tools"},
        {"name": "SubElectronics", "parent_name": "Electronics"},
        {"name": "SubTools", "parent_name": "Tools"},
        {"name": "SubTools2", "parent_name": "Tools"},
        {"name": "SubMachinery", "parent_name": "Machinery"},
    ]
    categories: InsertManyResult = await Category.insert_many(
        [Category(**category) for category in category_data]
    )
    yield categories
