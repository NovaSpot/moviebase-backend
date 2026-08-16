import os
from fastapi import FastAPI
from pydantic import BaseModel
import redis.asyncio as redis

app = FastAPI();


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"), decode_responses=True)

class Movie(BaseModel):
    id: str
    title: str
    year: str
    rating: str
    description: str
    thumbnail: str
    videoUrl: str

@app.get("/")
async def root():
    return {"status": "ok", "message": "FastAPI + Redis backend is running!"}

# 1. Add a movie
@app.post("/movies")
async def add_movie(movie: Movie):
    await r.hset(f"movie:{movie.id}", mapping=movie.model_dump())
    await r.sadd("movie_ids", movie.id)
    return {"message": "Saved", "movie": movie}

# 2. Get all movies
@app.get("/movies")
async def get_movies():
    ids = await r.smembers("movie_ids")
    movies = []
    for movie_id in ids:
        data = await r.hgetall(f"movie:{movie_id}")
        if data:
            movies.append(data)
    return movies

# 3. Get one movie by id
@app.get("/movies/{id}")
async def get_movie(id: str):
    data = await r.hgetall(f"movie:{id}")
    if not data:
        return {"id": id, "status": "not found"}
    return data
