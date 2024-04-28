import httpx
import asyncio
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from bs4 import BeautifulSoup
import logging
from resources.config import configure_logging, get_config

configure_logging()

app_config = get_config("config/app.json")
loader_ctx = get_config(app_config["loader"]["config"])

client = httpx.AsyncClient(
    headers={
        "User-Agent": "learningProject",
    },
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger("parser")


@app.get("/load_image")
async def load_image(count: int, exp_delay: int = 1):
    os.makedirs("images", exist_ok=True)
    for _ in range(0, count):
        link = f"{app_config['query']['link']}/get_from_queue"
        try:
            link = await client.get(link, timeout=httpx.Timeout(None))
            response = await client.get(link)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                div_link = soup.find("div", class_="market_listing_largeimage")
                image_link = div_link.find("img").get("src")
                response = await client.get(image_link)
                if response.status_code == 200:
                    image_filename = link.split("/")[-1] + ".jpg"
                    with open(
                        os.path.join("images", image_filename), "wb"
                    ) as image_file:
                        image_file.write(response.read())
                    logging.info(f"Изображение {link} сохранено как {image_filename}")

            else:
                logging.error(f"{response.status_code} при парсинге страницы {link}")
                await asyncio.sleep(exp_delay)
                return await load_image(link, exp_delay * 2)
        except Exception as ex:
            logging.error(f"{ex}")
            await asyncio.sleep(exp_delay)
            return await load_image(link, exp_delay * 2)
    return Response("Image saved", media_type="text/plain")


@app.get(
    "/get-image",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def get_image(image_name: str):
    try:
        with open(os.path.join("images", image_name), "rb") as image_file:
            content = image_file.read()
        return Response(content, media_type="image/png")
    except FileNotFoundError:
        logging.error(f"Файл {image_name} не найден")
        raise HTTPException(status_code=404, detail="File not found")
