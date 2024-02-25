import config
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = config.MONGO_URL
DB_NAME = config.DB_NAME

client = AsyncIOMotorClient(MONGO_URL)
db = client.DB_NAME
parts_collection = db.parts
category_collection = db.categories
parts_collection.create_index("serial_number", unique=True)
category_collection.create_index("name", unique=True)
