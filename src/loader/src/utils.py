import httpx
import os
import asyncio
import logging
from bs4 import BeautifulSoup
from fastapi import Response


async def load_image(client: httpx.AsyncClient, link: str, exp_delay: int = 1):
    try:
        response = await client.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            div_link = soup.find("div", class_="market_listing_largeimage")
            image_link = div_link.find("img").get("src")
            response = await client.get(image_link)
            if response.status_code == 200:
                image_filename = link.split("/")[-1] + ".jpg"
                with open(os.path.join("images", image_filename), "wb") as image_file:
                    image_file.write(response.read())
                logging.info(f"Изображение {link} сохранено как {image_filename}")
                return Response("Image saved", media_type="text/plain")
        else:
            logging.error(f"{response.status_code} при парсинге страницы {link}")
            await asyncio.sleep(exp_delay)
            return await load_image(link, exp_delay * 2)
    except Exception as ex:
        logging.error(f"{ex}")
        await asyncio.sleep(exp_delay)
        return await load_image(link, exp_delay * 2)


async def worker(client: httpx.AsyncClient, queue_str: str):
    while True:
        links = await client.get(f"{queue_str}/get_from_queue")
        await load_image(client, links, 1)
        client.post(f"{queue_str}/task_done", timeout=httpx.Timeout(None))
        await asyncio.sleep(2.0)
