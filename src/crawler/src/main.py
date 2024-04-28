import httpx
from fastapi import FastAPI
from resources.config import get_config, configure_logging
import logging
from utils import pages_link


configure_logging()

app_config = get_config("config/app.json")
steam_ctx = get_config(app_config["crawler"]["config"])

app = FastAPI()

logger = logging.getLogger("crawler")

client = httpx.Client(
    headers={
        "User-Agent": "learningProject",
    }
)


@app.post("/scrape")
async def scrape(count: int):
    await pages_link(client, steam_ctx, logger, app_config["query"]["link"], count)
    return {"status": f"GET {app_config['query']["link"]}  {"baoba"}"}
