from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field
from beanie import Document, PydanticObjectId



class APIError(BaseModel):
    code: int
    message: str
    request: Optional[Dict[str, str]] = None
    details: Optional[Dict[str, str]] = None

class QueryRoleType(str):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"

class Prompt(BaseModel):
    role: QueryRoleType
    content: str
    class Config:
        arbitrary_types_allowed = True

class Conversation(BaseModel):
    id: str = Field(..., read_only=True)
    name: str = Field(..., max_length=10)
    params: Optional[Dict[str, str]] = {}
    tokens: int = Field(..., read_only=True, gt=0)


class ConversationFull(BaseModel):
    id: str = Field(..., read_only=True)
    name: str = Field(..., max_length=200)
    params: Dict[str, str]
    tokens: int = Field(..., read_only=True, gt=0)
    messages: List[Prompt]

class ConversationPOST(BaseModel):
    name: str = Field(..., max_length=200)
    params: Optional[Dict[str, str]] = None

class ConversationPUT(BaseModel):
    name: str = Field(max_length=200)
    params: Dict[str, str] = None


class ConversationInfo(Document):
    id: str
    name: str = Field(..., max_length=200)
    params: Optional[Dict[str, str]] = {}
    tokens: Optional[int] = Field(None, gt=0)
    messages: Optional[List[Prompt]] = []

    class Settings:
        collection = "conversation_info"
