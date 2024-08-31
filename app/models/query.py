import uuid
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId

from datetime import datetime

class Query(BaseModel):
    query: str
    response: str
    timestamp: datetime

class QueryDocument(Document, Query):
    class Settings:
        collection = "queries"
    id: PydanticObjectId = None