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

from utils import generate_answer
from schemas import APIError, QueryRoleType, Prompt, Conversation, ConversationFull, ConversationPOST, ConversationPUT, ConversationInfo


app = FastAPI()

@app.on_event("startup")
async def lifespan():
    # Start the database connection
    await startup_db_client()


@app.get("/")
def root():
    return {"message": "Hello, I am a Chatbot!"}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content=APIError(code=400,
                         message="Invalid parameters provided")
    )

@app.post("/conversations", tags=["Conversations"])
async def create_new_conversation(conversation_post : ConversationPOST):
    """
    creates a conversation with LLM
    """
    try:
        uuid_num = uuid.uuid4()
        params = conversation_post.params if conversation_post.params is not None else {}

        conversation_info_db = ConversationInfo(
            id=str(uuid_num),
            name=conversation_post.name,
            params=params,
            tokens= 4096, #default
            messages=[] 
        )
        
        #insert into the db
        await conversation_info_db.insert()

        return JSONResponse( status_code=201, content= {"id": str(uuid_num)})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,
                            message="Internal server error")
        )


@app.get("/conversations", tags=["Conversations"])
async def retrieve_conversations():
    """
    retrieves a user conversation
    """
    try:
        #retrieve all conversations from db
        conversation_info = await ConversationInfo.find_all().to_list()

        return JSONResponse( status_code=200, content= conversation_info)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,
                            message="Internal server error")
        )
    

@app.put("/conversations/{id}", response_model=None)
async def update_existing_conversation(conversation: ConversationPUT):
    """
    updates llm properties of a conversation
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)
    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,
                                 message="Specified resource(s) was not found")
            )

    try:
        conversation_info.name = conversation_info.name
        conversation_info.params = conversation.params
        return JSONResponse( status_code=204, content= "Sucessfully updated.")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,
                            message="Internal server error")
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
                detail=APIError(code=404,
                                 message="Specified resource(s) was not found")
            )

    try:
        #get conversation histoy 
        conversation_history = conversation_info.messages
        return JSONResponse( status_code=200, content= conversation_history)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,
                            message="Internal server error")
        )

@app.delete("/conversations/{id}", tags = ["Conversations"])
async def delete_conversation():
    """
    deletes conversation
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)
    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail=APIError(code=404,
                                 message="Specified resource(s) was not found")
            )

    try:
        await conversation_info.delete()
        return JSONResponse( status_code=204, content= "Successfully deleted conversation.")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,
                            message="Internal server error")
        )


@app.post("/queries", tags =['LLM Queries'])
async def post_queries(id_num: str,
                       prompt: Prompt):
    """
    sends prompt to llm
    """
    try:
        conversation_info = await ConversationInfo.find_one(ConversationInfo.id == id)
    except Exception as e:
        raise HTTPException(
                status_code=404,
                detail= APIError(code=404,
                                 message="Specified resource(s) was not found")
            )
    try:
        answer = await generate_answer(prompt.content)
        try:
            #add to db
            a = 1 
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=APIError(code=422,
                                message="Unable to create resource")
            )

        return JSONResponse( status_code=201, content= {"id": id_num})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=APIError(code=500,
                            message="Internal server error")
        )



