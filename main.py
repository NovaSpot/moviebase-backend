import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
import redis.asyncio as redis
import boto3
from botocore.client import Config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

# --- Backblaze B2 (S3-compatible) setup ---
B2_ENDPOINT = os.getenv("B2_ENDPOINT")          # e.g. "https://s3.us-west-004.backblazeb2.com"
B2_KEY_ID = os.getenv("B2_KEY_ID")
B2_APP_KEY = os.getenv("B2_APP_KEY")
B2_BUCKET = os.getenv("B2_BUCKET")
B2_URL_EXPIRY = int(os.getenv("B2_URL_EXPIRY", "3600"))  # seconds, default 1hr

s3 = boto3.client(
    "s3",
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=B2_KEY_ID,
    aws_secret_access_key=B2_APP_KEY,
    config=Config(signature_version="s3v4"),
)

def presign(key: str) -> str:
    if not key:
        return ""
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": B2_BUCKET, "Key": key},
        ExpiresIn=B2_URL_EXPIRY,
    )

class Movie(BaseModel):
    id: str
    title: str
    year: str
    rating: str
    description: str
    thumbnail: str   # store as B2 object key, e.g. "movies/id/thumb.jpg"
    videoUrl: str     # store as B2 object key, e.g. "movies/id/video.mp4"

@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI + Redis backend is running!"}

# 1. Add a movie
@app.post("/movies")
async def add_movie(movie: Movie):
    await r.hset(f"movie:{movie.id}", mapping=movie.model_dump())
    await r.sadd("movie_ids", movie.id)
    return {"message": "Saved", "movie": movie}

# 2. Get all movies (with signed URLs)
@app.get("/movies")
async def get_movies():
    ids = await r.smembers("movie_ids")
    movies = []
    for movie_id in ids:
        data = await r.hgetall(f"movie:{movie_id}")
        if data:
            data["thumbnail"] = presign(data.get("thumbnail", ""))
            data["videoUrl"] = presign(data.get("videoUrl", ""))
            movies.append(data)
    return movies

# 3. Get one movie by id (with signed URLs)
@app.get("/movies/{id}")
async def get_movie(id: str):
    data = await r.hgetall(f"movie:{id}")
    if not data:
        return {"id": id, "status": "not found"}
    data["thumbnail"] = presign(data.get("thumbnail", ""))
    data["videoUrl"] = presign(data.get("videoUrl", ""))
    return data