from typing import Dict
from unittest.mock import ANY

import pytest
from fastapi import status
from httpx import AsyncClient, Response

from src.core.models.auth.user import User

expired_token: str = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjVmZDZiZTUyMjBiOWVhYzkwNzllMjEwIiwiZXhwI"
    "joxNzExMTA0Njg4fQ.gQa6XCAIKBK827wVZNgVeYLJZW4O6Yr5BHITBLLPr50"
)


@pytest.mark.anyio
async def test_get_token_correct_user(client: AsyncClient, user: User):
    # Arrange
    data: str = f"username={user['username']}&password={user['password']}"
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    expected_response: Dict[str, str] = {"access_token": ANY, "token_type": "bearer"}
    # Act
    response: Response = await client.post("/auth/token", content=data, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_response


@pytest.mark.anyio
async def test_get_token_incorrect_user(client: AsyncClient):
    # Arrange
    data: str = "username=IdoNotExist&password=Password"
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    expected_response: Dict[str, str] = {"detail": "Invalid credentials"}
    # Act
    response: Response = await client.post("/auth/token", content=data, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_response


@pytest.mark.anyio
async def test_register_new_user(client: AsyncClient):
    # Arrange
    data = {
        "username": "nonexistent_username",
        "email": "nonexistent_email@example.com",
        "password": "password",
    }
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    expected_response: Dict[str, str] = {
        "message": "User created",
    }
    # Act
    response: Response = await client.post("/auth/register", json=data, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    assert response.json() == expected_response


@pytest.mark.anyio
async def test_register_existing_username(client: AsyncClient, user: User):
    # Arrange
    data = {
        "username": user["username"],
        "email": "example_emai@email.com",
        "password": "password",
    }
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    expected_response: Dict[str, str] = {
        "detail": f"User with {{'username': '{user['username']}'}} already exists"
    }
    # Act
    response: Response = await client.post("/auth/register", json=data, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == expected_response


@pytest.mark.anyio
async def test_register_existing_email(client: AsyncClient, user: User):
    # Arrange
    data = {"username": "new_username", "email": user["email"], "password": "password"}
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

    expected_response: Dict[str, str] = {
        "detail": f"User with {{'email': '{user['email']}'}} already exists"
    }
    # Act
    response: Response = await client.post("/auth/register", json=data, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_409_CONFLICT

    assert response.json() == expected_response


@pytest.mark.parametrize(
    "endpoint", ("/categories/123", "/parts/123", "/search/parts", "search/categories")
)
@pytest.mark.anyio
async def test_GET_endpoints_valid_token(
    client: AsyncClient, token: str, endpoint: str
):
    # Arrange
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    expected_response: Dict[str, str] = {"detail": "Not authenticated"}
    # Act
    response: Response = await client.get(endpoint, headers=headers)
    # Assert
    assert response.status_code != status.HTTP_401_UNAUTHORIZED

    assert response.json() != expected_response


@pytest.mark.parametrize(
    "endpoint", ("/categories/123", "/parts/123", "/search/parts", "search/categories")
)
@pytest.mark.anyio
async def test_GET_endpoints_expired_token(client: AsyncClient, endpoint: str):
    # Arrange
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {expired_token}",
    }
    expected_response: Dict[str, str] = {"detail": "Signature has expired"}
    # Act
    response: Response = await client.get(endpoint, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == expected_response


@pytest.mark.parametrize("endpoint", ("/categories", "/parts"))
@pytest.mark.anyio
async def test_POST_endpoints_expired_token(client: AsyncClient, endpoint: str):
    # Arrange
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {expired_token}",
    }
    expected_response: Dict[str, str] = {"detail": "Signature has expired"}
    # Act
    response: Response = await client.post(endpoint, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == expected_response


@pytest.mark.parametrize("endpoint", ("/categories/123", "/parts/123"))
@pytest.mark.anyio
async def test_PUT_endpoints_expired_token(client: AsyncClient, endpoint: str):
    # Arrange
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {expired_token}",
    }
    expected_response: Dict[str, str] = {"detail": "Signature has expired"}
    # Act
    response: Response = await client.put(endpoint, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == expected_response


@pytest.mark.parametrize("endpoint", ("/categories/123", "/parts/123"))
@pytest.mark.anyio
async def test_DELETE_endpoints_expired_token(client: AsyncClient, endpoint: str):
    # Arrange
    headers: Dict[str, str] = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {expired_token}",
    }
    expected_response: Dict[str, str] = {"detail": "Signature has expired"}
    # Act
    response: Response = await client.delete(endpoint, headers=headers)
    # Assert
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == expected_response
