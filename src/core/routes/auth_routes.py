from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import DuplicateKeyError

from ..auth.jwt_handler import AuthHandler
from ..models.auth.token import Token
from ..models.auth.user import User

auth_handler: AuthHandler = AuthHandler()
router: APIRouter = APIRouter()


@router.post("/register", description="Register")
async def register(user_data: User):
    user_data.password = auth_handler.get_password_hash(user_data.password)
    try:
        user: User = await user_data.create()  # noqa
    except DuplicateKeyError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'User with {e.details.get("keyValue")} already exists',
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "message": "User created",
        },
    )


@router.post("/token", description="Login to get token")
async def get_token(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user: User = await User.find_one({"username": user_data.username})
    if not user or not auth_handler.verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token: str = auth_handler.encode_token(user.id)
    return Token(access_token=token, token_type="bearer")
