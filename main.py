import os
from fastapi import FastAPI
from pydantic import BaseModel
import redis.asyncio as redis

app = FastAPI()
r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

class Item(BaseModel):
    key: str
    value: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI + Redis backend is running!"}

# 1. Input / Set data
@app.post("/set")
async def set_key(item: Item):
    await r.set(item.key, item.value)
    return {"message": "Saved", "key": item.key, "value": item.value}

# 2. Fetch / Get data
@app.get("/get/{key}")
async def get_key(key: str):
    data = await r.get(key)
    if data is None:
        return {"key": key, "value": None, "status": "empty"}
    return {"key": key, "value": data, "status": "found"}
