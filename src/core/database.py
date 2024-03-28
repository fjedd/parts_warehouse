from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

import core.models as models

from .config import settings

MONGO_URL: str = settings.MONGO_URL
DB_NAME: str = settings.DB_NAME


class Database:
    client: AsyncIOMotorClient = AsyncIOMotorClient(f"{MONGO_URL}/{DB_NAME}")

    async def init_db(self) -> None:
        await init_beanie(
            database=self.client.get_default_database(), document_models=models.__all__
        )

    def close_db(self) -> None:
        self.client.close()
