import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    MONGO_URL: str = os.environ.get("MONGO_URL", "")
    DB_NAME: str = os.environ.get("DB_NAME", "")

    JWT_SECRET: str = os.environ.get("SECRET", "")
    JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", 15)  # type: ignore
    APP_PORT: int = os.environ.get("APP_PORT")  # type: ignore


settings = Settings()
