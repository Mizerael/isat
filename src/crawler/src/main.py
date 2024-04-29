import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resources.config import get_config, configure_logging
import logging
from utils import pages_link


configure_logging()

app_config = get_config("config/app.json")
steam_ctx = get_config(app_config["crawler"]["config"])

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("crawler")

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    }
)


@app.post("/scrape")
async def scrape(count: int):
    await pages_link(
        http_session=client,
        ctx=steam_ctx,
        logger=logger,
        queue_link=app_config["query"]["link"],
        count_items=count,
    )
    return {"status": f"GET {app_config['query']["link"]}  {"baoba"}"}
