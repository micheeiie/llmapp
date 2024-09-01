import motor.motor_asyncio
import os
from beanie import init_beanie
from app.schemas import ConversationInfo

# Define the global db_client variable
db_client = None

async def startup_db_client():
    global db_client  
    user = os.environ.get('MONGO_INITDB_ROOT_USERNAME', '')
    password = os.environ.get('MONGO_INITDB_ROOT_PASSWORD', '')
    database_name = os.environ.get('MONGO_INITDB_DATABASE', '')

    # Initialize the MongoDB client with the given credentials
    db_client = motor.motor_asyncio.AsyncIOMotorClient(f'mongodb://{user}:{password}@mongodb:27017')
    database = db_client[database_name]
    
    # Initialize Beanie with the document models
    await init_beanie(database, document_models=[ConversationInfo])
    print("Database connected successfully.")

# async def shutdown_db_client():
#     global db_client  
#     if db_client:
#         db_client.close()  # Close the MongoDB client connection
#         print("Database connection closed.")
