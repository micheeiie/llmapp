from fastapi import FastAPI, HTTPException
from typing import List, Optional, Dict, Union
from pydantic import BaseModel
from utils import generate_answer
from fastapi.responses import JSONResponse

import os
from dotenv import load_dotenv
import json
import openai
import uuid 
from pydantic import BaseModel, Field
from schemas import APIError, QueryRoleType, Prompt, Conversation, ConversationFull, ConversationPOST, ConversationPUT


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello, I am a Chatbot!"}


@app.post("/conversations", tags=["Conversations"])
async def create_new_conversation(conversation_post : ConversationPOST):
    """
    creates a conversation with LLM
    """
    uuid_num = uuid.uuid4()
    user = conversation_post.name
    # save uuid into ConversationsPOST
    return f"Hi, {user} with uuid:'{uuid_num}' created a chat."


@app.get("/conversations", tags=["Conversations"])
async def retrieve_conversations():
    """
    retrieves a user conversation
    """
    try:
        #retrieve from mongodb
        conversations_dct = {}

        return JSONResponse( status_code=200, content= conversations_dct)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 500, "message": "Internal server error"}
        )
    

@app.put("/conversations/{id}", response_model=None)
async def update_existing_conversation(conversation: ConversationPUT):
    """
    updates llm properties of a conversation
    """

    # if not in db, 
    #     raise HTTPException(
    #             status_code=404,
    #             detail={"code": 404, "message": "Specified resource(s) was not found"}
    #         )

    try:
        #get conversation params using id
        #update the params
        return JSONResponse( status_code=204, content= "sucessfully updated")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 500, "message": "Internal server error"}
        )
    

@app.get("/conversations/{id}", tags=["Conversations"])
async def retrieve_conversation(id: str):
    """
    retrieves conversaton history
    """
    # if not in db, 
    #     raise HTTPException(
    #             status_code=404,
    #             detail={"code": 404, "message": "Specified resource(s) was not found"}
    #         )

    try:
        #get conversation histoy 
        conversation = {}
        return JSONResponse( status_code=200, content= conversation)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 500, "message": "Internal server error"}
        )

@app.delete("/conversations/{id}", tags = ["Conversations"])
async def delete_conversation():
    """
    deletes conversation
    """
    # if not in db, 
    #     raise HTTPException(
    #             status_code=404,
    #             detail={"code": 404, "message": "Specified resource(s) was not found"}
    #         )

    try:
        # delete conversation from db
        return JSONResponse( status_code=204, content= "Successfully deleted conversation.")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 500, "message": "Internal server error"}
        )


@app.post("/queries", tags =['LLM Queries'])
async def post_queries(id_num: str,
                       prompt: Prompt):
    """
    sends prompt to llm
    """
    # if not in db, 
    #     raise HTTPException(
    #             status_code=404,
    #             detail={"code": 404, "message": "Specified resource(s) was not found"}
    #         )

    try:
        answer = await generate_answer(prompt.content)
        try:
            #add to db
            a = 1 
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail={"code": 422, "message": "Unable to create resource"}
            )

        return JSONResponse( status_code=201, content= {"id": id_num})
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"code": 500, "message": "Internal server error"}
        )



