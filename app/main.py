from fastapi import FastAPI, Body, Request
from contextlib import asynccontextmanager

from typing import List

from app.models.query import Query, QueryDocument
from app.database import startup_db_client

app = FastAPI()

@app.on_event("startup")
async def lifespan():
    # Start the database connection
    await startup_db_client()

@app.get("/")
async def root():
    return {"message": "Test"}

@app.get("/hello")
async def test():
    return {"message": "Hello"}

@app.post("/submit_query", response_description="Query added into the database")
async def submit_query(query: Query = Body(...)):
    query_doc = QueryDocument(**query.dict())
    await query_doc.insert()
    return query

@app.get("/list_queries", response_description="List addresses", response_model=List[Query])
async def get_queries():
    queries = await QueryDocument.find_all().to_list()
    return queries