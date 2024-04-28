import httpx
import asyncio
from fastapi.responses import Response
from bs4 import BeautifulSoup
import logging


async def load_image(client: httpx.AsyncClient, link: str, exp_delay: int = 1):
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
            return await load_image(link, exp_delay * 2)
    except Exception as ex:
        logging.error(f"{ex}")
        await asyncio.sleep(exp_delay)
        return await load_image(link, exp_delay * 2)


async def worker(client: httpx.AsyncClient, queue_link: str):
    while True:
        link = await client.get(queue_link)
        await load_image(client, link, 1)
        await asyncio.sleep(2.0)
