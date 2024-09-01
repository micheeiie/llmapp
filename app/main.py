from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, ValidationError
from app.database import startup_db_client

import os
import json
import uuid
import openai

from app.utils import generate_answer
from app.schemas import APIError, QueryRoleType, Prompt, Conversation, ConversationFull, ConversationPOST, ConversationPUT, ConversationInfo, Queries


app = FastAPI()

@app.on_event("startup")
async def lifespan():
    # Start the database connection
    await startup_db_client()


@app.get("/")
def root():
    return {"message": "Hello, I am a Chatbot!"}

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=APIError(code=400, message="Invalid parameters provided").dict()
    )

@app.post("/conversations", tags=["Conversations"])
async def create_new_conversation(conversation_post : ConversationPOST):
    """
    creates a conversation with LLM
    """
    try:
        uuid_num = str(uuid.uuid4())
        params = conversation_post.params if conversation_post.params is not None else {}

        conversation_info_doc = ConversationInfo(
            id=str(uuid_num),
            name=conversation_post.name,
            params=params,
            tokens= 4096, #default
            messages=[] 
        )
        
        # Insert the document into the database
        await conversation_info_doc.insert()
        return JSONResponse( status_code=201, content={"id": str(uuid_num)})
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error").dict()
        )
        
    
@app.get("/conversations", tags=["Conversations"])
async def retrieve_conversations():
    """
    Retrieves all user conversations.
    """
    try:
        # Retrieve all conversations from the database
        conversation_info = await ConversationInfo.find_all().to_list()
        return JSONResponse(status_code=200, content=conversation_info)
    
    except Exception:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error").dict()
        )
    

@app.put("/conversations/{id}")
async def update_existing_conversation(id: str, conversation: ConversationPUT):
    """
    Updates the LLM properties of a conversation.
    """
    conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    if conversation_info is None:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,message="Specified resource(s) was not found").dict()
            )

    try:
        conversation_info.name = conversation_info.name
        conversation_info.params = conversation.params
        await conversation_info.save()
        return JSONResponse(status_code=204)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,message="Internal server error").dict()
        )
    

@app.get("/conversations/{id}", tags=["Conversations"])
async def retrieve_conversation(id: str):
    """
    retrieves conversaton history
    """

    conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    if conversation_info is None:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,message="Specified resource(s) was not found").dict()
            )

    try:
        # Get conversation history
        conversation_history = conversation_info.messages
        return JSONResponse(status_code=200, content=conversation_history)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error").dict()
        )

@app.delete("/conversations/{id}", tags = ["Conversations"])
async def delete_conversation(id: str):
    """
    Deletes a conversation by ID.
    """
    conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    if conversation_info is None:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,message="Specified resource(s) was not found").dict()
            )

    try:
        await conversation_info.delete()
        return JSONResponse(status_code=204)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error")).dict()


@app.post("/queries", tags =['LLM Queries'])
async def post_queries(queries: Queries):
    """
    Sends a prompt to the LLM and updates the conversation.
    """
    conversation_info = await ConversationInfo.find_one(ConversationInfo.id == queries.id)

    if conversation_info is None:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,message="Specified resource(s) was not found").dict()
            )
    try:
        # Generate the answer using the LLM
        parameters = conversation_info.params
        answer = generate_answer(queries.prompt.content, queries.prompt.messages, parameters)

        try:
            # Update the conversation messages
            currentChat = [{"role":"user",
                           "content": queries.prompt.content},
                           {"role":"assistant",
                            "content":answer}]
            
            conversation_info.messages = conversation_info.messages.append(currentChat)

            conversation_info.save()

        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=APIError(code=422, message="Unable to create resource").dict()
            )

        return JSONResponse( status_code=201, content={"id": queries.id})
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error").dict()
        )



