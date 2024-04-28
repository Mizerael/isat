import httpx
from fastapi import FastAPI
import logging
from resources.config import configure_logging, get_config
from utils import load_image

configure_logging()

app_config = get_config("config/app.json")

logger = logging.getLogger("app")

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
async def scrape(count: int):
    post_link = f"{app_config['crawler']['link']}/scrape?count={count}"
    timeout = httpx.Timeout(None)
    await client.post(url=post_link, timeout=timeout)
    await load_image(app_config["loader"]["link"], logger, count)

    return {"message": app_config["loader"]["link"]}
