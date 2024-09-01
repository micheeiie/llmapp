from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, ValidationError
from database import startup_db_client, shutdown_db_client
from contextlib import asynccontextmanager
import os
import json
import uuid
import openai
from utils import generate_answer
from schemas import APIError, QueryRoleType, Prompt, Conversation, ConversationFull, ConversationPOST, ConversationPUT, ConversationInfo

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the database connection
    await startup_db_client()
    yield
    await shutdown_db_client()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Hello, I am a Chatbot!"}

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=APIError(code=400, message="Invalid parameters provided")
    )

@app.post("/conversations", tags=["Conversations"])
async def create_new_conversation(conversation_post : ConversationPOST):
    """
    creates a conversation with LLM
    """
    try:
        uuid_num = str(uuid.uuid4())
        params = conversation_post.params if conversation_post.params is not None else {}

        conversation_info_db = ConversationInfo(
            id=str(uuid_num),
            name=conversation_post.name,
            params=params,
            tokens= 4096, #default
            messages=[] 
        )
        
        # Insert the document into the database
        await conversation_info_db.insert()
        return JSONResponse( status_code=201, content= {"id": str(uuid_num)})
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error")
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
            detail=APIError(code=500, message="Internal server error")
        )
    

@app.put("/conversations/{id}")
async def update_existing_conversation(conversation: ConversationPUT):
    """
    Updates the LLM properties of a conversation.
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404, message="Specified resource(s) was not found")
                )

    try:
        conversation_info.name = conversation_info.name
        conversation_info.params = conversation.params
        await conversation_info.save()
        return JSONResponse(status_code=204, content= "Sucessfully updated.")
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,message="Internal server error")
        )
    

@app.get("/conversations/{id}", tags=["Conversations"])
async def retrieve_conversation(id: str):
    """
    retrieves conversaton history
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,message="Specified resource(s) was not found")
            )

    try:
        # Get conversation history
        conversation_history = conversation_info.messages
        return JSONResponse(status_code=200, content= conversation_history)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error")
        )

@app.delete("/conversations/{id}", tags = ["Conversations"])
async def delete_conversation():
    """
    Deletes a conversation by ID.
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404, message="Specified resource(s) was not found")
            )

    try:
        await conversation_info.delete()
        return JSONResponse(status_code=204, content= "Successfully deleted conversation.")
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error"))


@app.post("/queries", tags =['LLM Queries'])
async def post_queries(id_num: str,
                       prompt: Prompt):
    """
    Sends a prompt to the LLM and updates the conversation.
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)

    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail= APIError(code=404, message="Specified resource(s) was not found")
            )
    try:
        # Generate the answer using the LLM
        parameters = conversation_info.params
        answer = await generate_answer(prompt.content, parameters)

        try:
            # Update the conversation messages
            currentChat = [{"role":"user",
                           "content": prompt.content},
                           {"role":"assistant",
                            "content":answer}]
            
            conversation_info.messages = conversation_info.messages.append(currentChat)
            conversation_info.save()

        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=APIError(code=422, message="Unable to create resource")
            )

        return JSONResponse( status_code=201, content= {"id": id_num})
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500, message="Internal server error")
        )



