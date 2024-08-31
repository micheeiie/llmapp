import motor
import os
from beanie import init_beanie

from app.models.query import QueryDocument

async def startup_db_client():
    user = os.environ.get('MONGO_INITDB_ROOT_USERNAME', '')
    password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD', '')
    database_name = os.environ.get('MONGO_INITDB_DATABASE', '')

    client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://{user}:{password}@mongodb:27017')
    database = client[database_name]
    await init_beanie(database, document_models=[QueryDocument])
