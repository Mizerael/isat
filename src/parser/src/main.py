import httpx
import asyncio
from fastapi import FastAPI
from fastapi.responses import Response
from bs4 import BeautifulSoup
import logging
from resources.config import configure_logging, get_config

configure_logging()

app_config = get_config("config/app.json")

logger = logging.getLogger("app")

app = FastAPI()

logger = logging.getLogger("parser")

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    },
)


@app.get(
    "/get-image",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def load_images(link: str, exp_delay: int = 1):
    try:
        response = await client.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            div_link = soup.find("div", class_="market_listing_largeimage")
            image_link = div_link.find("img").get("src")
            response = await client.get(image_link)
            if response.status_code == 200:
                return Response(response.read(), media_type="image/png")
        else:
            logging.error(f"{response.status_code} при парсинге страницы {link}")
            await asyncio.sleep(exp_delay)
            return await load_images(link, exp_delay * 2)
    except Exception as ex:
        logging.error(f"{ex}")
        await asyncio.sleep(exp_delay)
        return await load_images(link, exp_delay * 2)
