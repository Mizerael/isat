from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import asyncio
import pickle
import os
from contextlib import asynccontextmanager

QUEUE_FILENAME = "queue.pickle"

queue = asyncio.Queue()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.path.exists(QUEUE_FILENAME):
        with open(QUEUE_FILENAME, "rb") as f:
            queue._queue = pickle.load(f)
    yield
    with open(QUEUE_FILENAME, "wb") as f:
        pickle.dump(queue._queue, f)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    },
)


@app.get("/")
async def root():
    return {"message": "Aboba"}


@app.post("/add_to_queue")
async def add_to_queue(link: str):
    await queue.put(link)
    return "OK"


@app.get("/get_from_queue")
async def get_from_queue() -> str:
    link = await queue.get()
    return link
