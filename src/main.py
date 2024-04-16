import httpx
from fastapi import FastAPI
import logging
from resources.config import configure_logging, get_config

configure_logging()

app_config = get_config("config/app.json")

logger = logging.getLogger("app")
steam_ctx = get_config(app_config["cite"]["config"])


async def lifespan(api: FastAPI):
    return "aboba"


app = FastAPI()

logger = logging.getLogger("crapser")

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    },
)


@app.get("/")
async def root():
    return {"message": "Aboba"}


@app.post("/scrape")
async def scrape():
    return {"message": "Start Aboba"}
