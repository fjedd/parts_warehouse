from datetime import datetime, timedelta
from typing import Annotated, Any, Dict

from beanie import PydanticObjectId
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from ..config import settings
from ..models.auth.user import User


class AuthHandler:
    pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    secret: str = settings.JWT_SECRET
    algorithm: str = settings.JWT_ALGORITHM
    expire: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    oauth2_bearer: OAuth2PasswordBearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(password, hashed_password)

    def encode_token(self, user_id: PydanticObjectId) -> str:
        payload: Dict[str, Any] = {
            "user_id": user_id.__str__(),
            "exp": datetime.utcnow() + timedelta(minutes=self.expire),
        }
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)

    async def verify_token(self, token: Annotated[str, Depends(oauth2_bearer)]) -> User:
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            user_id: str = payload["user_id"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Signature has expired")
        except jwt.JWTError as e:
            raise HTTPException(status_code=401, detail=e.__str__())
        user: User = await User.get(user_id)
        if not user:
            raise HTTPException(
                status_code=401, detail="Could not verify token for this user"
            )
        return user
