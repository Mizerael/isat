import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
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
    await load_image(
        crawler_link=app_config["crawler"]["link"],
        loader_link=app_config["loader"]["link"],
        query_link=app_config["query"]["link"],
        logger=logger,
        count=count,
        count_worker=app_config["loader"]["count_worker"],
    )
    return "Ok"


@app.get(
    "/get_image",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_image(name: str):
    response = await client.get(
        f"{app_config['loader']['link']}/get_image?image_name={name}"
    )
    if response.status_code == 200:
        return response
    else:
        raise HTTPException(status_code=404, detail="File not found")
