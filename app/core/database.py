import config as config
import core.models as models
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = config.MONGO_URL
DB_NAME = config.DB_NAME


async def init_db():
    client = AsyncIOMotorClient(f"{MONGO_URL}/{DB_NAME}")
    await init_beanie(
        database=client.get_default_database(), document_models=models.__all__
    )
