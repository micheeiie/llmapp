from fastapi import Body, Request, HTTPException, status
from fastapi.encoders import jsonable_encoder

from app.models.query import Query

def get_collection_llm(request: Request):
  return request.app.mongodb

def create_query(request: Request, query: Query = Body(...)):
    query_data = jsonable_encoder(query)
    new_query = get_collection_llm(request).insert_one(query_data)
    created_query = get_collection_llm(request).find_one({"_id": new_query.inserted_id})
    return created_query

def list_queries(request: Request, limit: int):
    queries = list(get_collection_llm(request).find(limit = limit))
    return queries