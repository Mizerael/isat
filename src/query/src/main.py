from fastapi import FastAPI
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

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    },
)


@app.get("/")
async def root():
    return {"message": "Aboba"}


@app.post("/add_to_queue")
async def add_to_queue(links: list[str]):
    for link in links:
        queue.put_nowait(link)


@app.get("/get_from_queue")
async def get_from_queue() -> str:
    link = await queue.get()
    queue.task_done()
    return link
